-- PostgreSQL, not the UI, is the final authority on scheduling conflicts.
-- btree_gist is a trusted extension on PostgreSQL 14+.
CREATE EXTENSION IF NOT EXISTS btree_gist;
--> statement-breakpoint
ALTER TABLE trainer_slots ADD CONSTRAINT slots_no_trainer_overlap
  EXCLUDE USING gist (trainer_id WITH =, tstzrange(starts_at, ends_at, '[)') WITH &&)
  WHERE (cancelled_at IS NULL);
--> statement-breakpoint
ALTER TABLE bookings ADD CONSTRAINT bookings_no_member_overlap
  EXCLUDE USING gist (member_id WITH =, tstzrange(starts_at, ends_at, '[)') WITH &&)
  WHERE (status = 'confirmed');
--> statement-breakpoint
ALTER TABLE bookings ADD CONSTRAINT bookings_no_trainer_overlap
  EXCLUDE USING gist (trainer_id WITH =, tstzrange(starts_at, ends_at, '[)') WITH &&)
  WHERE (status = 'confirmed');
--> statement-breakpoint
CREATE FUNCTION enforce_booking_slot() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE slot trainer_slots%ROWTYPE;
BEGIN
  IF TG_OP = 'UPDATE' THEN
    IF (NEW.member_id, NEW.slot_id, NEW.trainer_id, NEW.starts_at, NEW.ends_at)
      IS DISTINCT FROM (OLD.member_id, OLD.slot_id, OLD.trainer_id, OLD.starts_at, OLD.ends_at)
      OR (OLD.status = 'cancelled' AND NEW.status <> 'cancelled') THEN
      RAISE EXCEPTION 'Booking identity and schedule are immutable' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
  END IF;

  SELECT * INTO slot FROM trainer_slots WHERE id = NEW.slot_id FOR UPDATE;
  IF NOT FOUND OR slot.cancelled_at IS NOT NULL
    OR (NEW.trainer_id, NEW.starts_at, NEW.ends_at) IS DISTINCT FROM (slot.trainer_id, slot.starts_at, slot.ends_at) THEN
    RAISE EXCEPTION 'Booking must match an available slot' USING ERRCODE = '23514';
  END IF;
  RETURN NEW;
END;
$$;
--> statement-breakpoint
CREATE TRIGGER bookings_validate_slot BEFORE INSERT OR UPDATE ON bookings
  FOR EACH ROW EXECUTE FUNCTION enforce_booking_slot();
--> statement-breakpoint
CREATE FUNCTION enforce_slot_update() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF (NEW.trainer_id, NEW.starts_at, NEW.ends_at) IS DISTINCT FROM (OLD.trainer_id, OLD.starts_at, OLD.ends_at)
    OR (OLD.cancelled_at IS NOT NULL AND NEW.cancelled_at IS NULL) THEN
    RAISE EXCEPTION 'Slot schedule is immutable; publish a new slot instead' USING ERRCODE = '23514';
  END IF;
  IF NEW.cancelled_at IS NOT NULL AND EXISTS (SELECT 1 FROM bookings WHERE slot_id = OLD.id AND status = 'confirmed') THEN
    RAISE EXCEPTION 'A booked slot cannot be withdrawn' USING ERRCODE = '23514';
  END IF;
  RETURN NEW;
END;
$$;
--> statement-breakpoint
CREATE TRIGGER slots_validate_update BEFORE UPDATE ON trainer_slots
  FOR EACH ROW EXECUTE FUNCTION enforce_slot_update();
