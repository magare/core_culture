/* =====================================================================
   CORE CULTURE — central content source (sample prototype data)
   ---------------------------------------------------------------------
   EVERYTHING the site renders about the business lives here.
   Fields marked  sample: true  / values marked "TBC" are PLACEHOLDERS
   for review only — they are NOT confirmed business facts.
   Imagery: brand art-direction crops from the concept work, NOT
   verified photographs of the final gym.
   Edit this file to publish real content.
   ===================================================================== */
window.CC = (function () {
  "use strict";

  /* ---- categories: one colour system for plan, carousel, timetable ---- */
  const categories = {
    strength:  { label: "Strength",  color: "#ff5a1f", deep: "#c43a06" },
    hybrid:    { label: "Hybrid / HYROX", color: "#ffb400", deep: "#8a5f00" },
    cardio:    { label: "Cardio & Engine", color: "#4f7dff", deep: "#2743b8" },
    studio:    { label: "Dance · Yoga", color: "#ff4fa3", deep: "#b81d6d" },
    recovery:  { label: "Recovery",  color: "#49c3d8", deep: "#0b7f95" },
    community: { label: "Community", color: "#8fbf6f", deep: "#44691f" }
  };

  /* ---- rooms: carousel order = walkthrough order; plan = SVG coords ----
     access: "included" | "bookable" | "tbc"                              */
  const rooms = [
    {
      id: "strength", num: "01", name: "Strength Zone", category: "strength",
      access: "included", accessNote: "Open with every membership — hours to confirm.",
      tagline: "Racks, platforms and iron that means it.",
      intro: "The lifting heart of the club: racks and platforms for barbell work, a machines bay for targeted, biomechanics-backed training.",
      photo: { src: "../crops/w303-floor-weights.jpg", alt: "Art-directed render: training machine and calibrated plates in the strength zone" },
      amenities: ["Squat racks", "Platforms", "Calibrated plates", "Dumbbells", "Benches"],
      facilities: [
        ["Floor", "Rubber platform flooring"], ["Racks & platforms", "TBC — count to confirm"],
        ["Plates", "Calibrated (kg)"], ["Chalk", "Provided"], ["Coached hours", "See timetable"]
      ],
      plan: { x: 40, y: 40, w: 330, h: 300, letter: "A" },
      gallery: [
        { src: "../crops/w303-floor-weights.jpg", alt: "Machine and plates in the strength zone — art direction", caption: "Machines bay — art direction" },
        { src: "../crops/w301-machine-sq.jpg", alt: "Close view of a selectorised training machine — art direction", caption: "Biomechanics-first machines" },
        { src: "../crops/w301-machine-tall.jpg", alt: "Tall crop of strength equipment against a pale wall — art direction", caption: "Iron, kept honest" }
      ],
      equipment: ["rack", "barbell", "plates", "dumbbells", "bench", "cables", "machines"]
    },
    {
      id: "hybrid", num: "02", name: "Hybrid Turf", category: "hybrid",
      access: "included", accessNote: "Open floor; HYROX batches use it on the timetable.",
      tagline: "Sled lanes and a turf track built for HYROX.",
      intro: "A functional floor for sled work, carries, ropes and race simulation — the training ground for HYROX batches and engine days.",
      photo: { src: "../crops/w301-sled-sq.jpg", alt: "Art-directed render: athlete driving a weighted sled across dark turf" },
      amenities: ["Sled track", "Turf lane", "Sleds & ropes", "Boxes", "HYROX stations"],
      facilities: [
        ["Surface", "Turf sprint lane"], ["Sleds", "Weighted, lane use"],
        ["HYROX rig", "Stations — layout TBC"], ["Best for", "HYROX prep · circuits · carries"]
      ],
      plan: { x: 390, y: 40, w: 250, h: 300, letter: "C" },
      gallery: [
        { src: "../crops/w301-sled-sq.jpg", alt: "Sled drive on the hybrid turf — art direction", caption: "Sled lane, race pace" },
        { src: "../crops/w301-sled-tall.jpg", alt: "Tall crop of a sled push — art direction", caption: "Low and driving" },
        { src: "../crops/w307-obj-sled.jpg", alt: "Close view of a sled handle — art direction", caption: "Grip points, chalk dust" }
      ],
      equipment: ["sled", "ropes", "boxes", "kettlebells", "hyrox"]
    },
    {
      id: "cardio", num: "03", name: "Engine Room", category: "cardio",
      access: "included", accessNote: "Open with every membership; class programming varies.",
      tagline: "Treadmills, ergs and bikes — running, upgraded.",
      intro: "Cardio that doesn't patronise you: platforms for zone-2 base, threshold work and sprint finishes, with screens you're allowed to ignore.",
      photo: { src: "../crops/w306-hero-streak.jpg", alt: "Art-directed image: light streaks suggesting pace on the engine room floor" },
      amenities: ["Treadmills", "Row ergs", "Ski ergs", "Bikes"],
      facilities: [
        ["Machines", "Count & models TBC"], ["Screens", "Training data — optional"],
        ["Programming", "Engine classes on the timetable"], ["Best for", "Base · threshold · HYROX engine"]
      ],
      plan: { x: 660, y: 40, w: 300, h: 130, letter: "D" },
      gallery: [
        { src: "../crops/w306-hero-streak.jpg", alt: "Light-streak artwork for the engine room — art direction", caption: "Pace, made visible" },
        { src: "../crops/p02-streaks.jpg", alt: "Colour light streaks — art direction", caption: "Interval lights" }
      ],
      equipment: ["treadmill", "rower", "ski", "bike"]
    },
    {
      id: "studio", num: "04", name: "The Studio", category: "studio",
      access: "included", accessNote: "Included classes; hobby clubs may run as events — see timetable.",
      tagline: "Dance, yoga and hobby clubs under club lights.",
      intro: "A sprung floor with a sound system and zero judgement: dance and zumba evenings, yoga flows, and hobby clubs for people who don't call it cardio.",
      photo: { src: "../crops/w303-floor-studio.jpg", alt: "Art-directed render: dancer in silhouette under pink studio light" },
      amenities: ["Sprung floor", "Sound system", "Club lights", "Yoga props"],
      facilities: [
        ["Floor", "Sprung — size TBC"], ["Lights", "Programmable studio wash"],
        ["Mirror wall", "TBC — to confirm"], ["Classes", "Dance · zumba · yoga · hobby clubs"]
      ],
      plan: { x: 660, y: 200, w: 300, h: 140, letter: "E" },
      gallery: [
        { src: "../crops/w303-floor-studio.jpg", alt: "Dancer under pink light — art direction", caption: "Choreography hour" },
        { src: "../crops/w301-hero-dance.jpg", alt: "Dancer between neon tubes — art direction", caption: "Club lights, zero mirrors policy TBC" },
        { src: "../crops/p01-dance.jpg", alt: "Dancer in silhouette, magenta wash — art direction", caption: "The last song nobody skips" }
      ],
      equipment: ["yoga", "av"]
    },
    {
      id: "recovery", num: "05", name: "Recovery Wing", category: "recovery",
      access: "bookable", accessNote: "Plunge and steam — booking model to confirm (included vs slot-paid).",
      tagline: "Ice bath and steam. Three honest minutes.",
      intro: "Cold plunge and steam for the work after the work. Guided immersion sessions run on the timetable; protocols are coached, not macho.",
      photo: { src: "../crops/w301-hero-ice.jpg", alt: "Art-directed render: ice water filling a cold plunge tub" },
      amenities: ["Cold plunge", "Steam", "Towels", "Guided sessions"],
      facilities: [
        ["Plunge", "Temperature TBC — protocol ~3 min"], ["Steam", "Capacity TBC"],
        ["Booking", "By slot — model TBC"], ["Coaching", "Breathing guided in sessions"]
      ],
      plan: { x: 390, y: 360, w: 180, h: 160, letter: "F" },
      gallery: [
        { src: "../crops/w301-hero-ice.jpg", alt: "Ice bath close-up — art direction", caption: "The tub doesn't lie" },
        { src: "../crops/w301-ice-sq.jpg", alt: "Ice and water — art direction", caption: "Cold, patient" },
        { src: "../crops/p10-ice.jpg", alt: "Black-and-white plunge study — art direction", caption: "Steam after" }
      ],
      equipment: ["plunge", "steam"]
    },
    {
      id: "lounge", num: "06", name: "The Lounge", category: "community",
      access: "included", accessNote: "Open to members during staffed hours — hours TBC.",
      tagline: "Work-lift balance. Coffee unmetered.",
      intro: "Meetings before the session, people after it. A warm room to work, argue about training and stay longer than you planned.",
      photo: { src: "../crops/p05-field.jpg", alt: "Art-directed render: a desk standing in an open field — the lounge as headspace" },
      amenities: ["Seats & desks", "Coffee", "Wi-Fi TBC", "No clocks"],
      facilities: [
        ["Seats", "Count TBC"], ["Coffee", "Included — machine TBC"],
        ["Work setup", "Desks & power — TBC"], ["Vibe", "Sessions end; culture doesn't"]
      ],
      plan: { x: 590, y: 360, w: 370, h: 160, letter: "G" },
      gallery: [
        { src: "../crops/p05-field.jpg", alt: "Desk in a field — lounge headspace artwork", caption: "Headspace, drawn literally" },
        { src: "../crops/w301-field-tall.jpg", alt: "Tall crop of the field desk artwork", caption: "Work-lift balance" }
      ],
      equipment: []
    },
    {
      id: "arrival", num: "07", name: "Arrival & Parking", category: "community",
      access: "included", accessNote: "Parking included with membership — to confirm at sign-up.",
      tagline: "Parking. Finally.",
      intro: "Drive in, park without a quest, walk in warm. The lot is part of the membership — arrival should never be the hardest set.",
      photo: { src: "../crops/w305-hero-park.jpg", alt: "Art-directed render: cars parked in rows at dusk" },
      amenities: ["On-site parking", "Step-free entry TBC", "Front desk", "Accessibility TBC"],
      facilities: [
        ["Spaces", "Count TBC — brand promise: plenty"], ["EV charging", "TBC"],
        ["Entry", "Reception & desk"], ["Access", "Step-free route — to confirm"]
      ],
      plan: { strip: true, letter: "P" },
      gallery: [
        { src: "../crops/w305-hero-park.jpg", alt: "Parked cars at dusk — art direction", caption: "No parking cardio required" },
        { src: "../crops/w301-dusk-wide.jpg", alt: "Parking at dusk, wide — art direction", caption: "Arrival, un-fought" }
      ],
      equipment: []
    },
    {
      id: "lobby", num: "00", name: "Lobby & Desk", category: "community",
      access: "included", accessNote: "Front desk during staffed hours.",
      tagline: "Start here. The desk knows your name eventually.",
      intro: "Reception, trial check-ins and the house board. First visit starts with a tour — book one below.",
      photo: { src: "../crops/w301-hero-frost.jpg", alt: "Art-directed texture: frosted glass — lobby detail study" },
      amenities: ["Reception", "House board", "Trial check-in"],
      facilities: [
        ["Desk hours", "Staffed hours TBC"], ["Tours", "Bookable with a trial"],
        ["Board", "Personal bests, posted honestly"]
      ],
      plan: { x: 40, y: 360, w: 200, h: 160, letter: "B" },
      gallery: [
        { src: "../crops/w301-hero-frost.jpg", alt: "Frosted glass texture — lobby detail artwork", caption: "Detail study — real photos to follow" }
      ],
      equipment: []
    }
  ];

  /* ---- equipment: beginner-first purpose; specs only where known ---- */
  const equipment = [
    { id: "rack", name: "Squat racks & platforms", category: "strength", roomId: "strength",
      purpose: "The safe way to squat, press and pull heavy — bars are caught at height if a rep fails.",
      brand: "TBC", specs: [["Units", "TBC"], ["Safety", "Spotter arms + platform drops"]], photo: null },
    { id: "barbell", name: "Olympic barbells", category: "strength", roomId: "strength",
      purpose: "The standard bar for the big lifts — squat, bench, deadlift, press.",
      brand: "TBC", specs: [["Weights", "TBC"], ["Coaching", "Barbell Club — see timetable"]], photo: null },
    { id: "plates", name: "Calibrated plates", category: "strength", roomId: "strength",
      purpose: "Weighted discs in precise increments, so progress is measured in kilos, not vibes.",
      brand: "TBC", specs: [["Range", "TBC"], ["Calibration", "Competition-style (kg)"]], photo: null },
    { id: "dumbbells", name: "Dumbbells", category: "strength", roomId: "strength",
      purpose: "Free weights for unilateral work — one arm or leg at a time, so imbalances can't hide.",
      brand: "TBC", specs: [["Range", "TBC"]], photo: null },
    { id: "bench", name: "Benches", category: "strength", roomId: "strength",
      purpose: "Stable platforms for pressing and supported rows.",
      brand: "TBC", specs: [["Units", "TBC"]], photo: null },
    { id: "cables", name: "Cable stations", category: "strength", roomId: "strength",
      purpose: "Smooth constant-tension pulleys for accessory work — rows, pulldowns, rotations.",
      brand: "TBC", specs: [["Stations", "TBC"]], photo: null },
    { id: "machines", name: "Selectorised machines", category: "strength", roomId: "strength",
      purpose: "Guided-path machines that target one muscle group — beginner-friendly and joint-honest.",
      brand: "TBC — biomechanics-backed line, to confirm", specs: [["Range", "TBC"]], photo: { src: "../crops/w301-machine-sq.jpg", alt: "Selectorised machine, close view — art direction" } },
    { id: "sled", name: "Weight sleds", category: "hybrid", roomId: "hybrid",
      purpose: "Push or pull a weighted sled — full-body power with zero impact on the joints.",
      brand: "TBC", specs: [["Lanes", "Turf track"], ["Use", "Open floor + Sled League"]], photo: { src: "../crops/w307-obj-sled.jpg", alt: "Sled handles, close view — art direction" } },
    { id: "ropes", name: "Battle ropes", category: "hybrid", roomId: "hybrid",
      purpose: "Fast wave drills that spike the heart rate and build grip and shoulder endurance.",
      brand: "TBC", specs: [], photo: null },
    { id: "boxes", name: "Plyo boxes", category: "hybrid", roomId: "hybrid",
      purpose: "Step-ups and explosive jumps at three honest heights.",
      brand: "TBC", specs: [], photo: null },
    { id: "kettlebells", name: "Kettlebells", category: "hybrid", roomId: "hybrid",
      purpose: "Swings, carries and flows — strength and engine work in one piece of iron.",
      brand: "TBC", specs: [["Range", "TBC"]], photo: null },
    { id: "hyrox", name: "HYROX simulation stations", category: "hybrid", roomId: "hybrid",
      purpose: "Race-specific stations — wall balls, lunges, pushes — laid out for full simulations.",
      brand: "TBC", specs: [["Batches", "HYROX Prep — see timetable"]], photo: null },
    { id: "treadmill", name: "Treadmills", category: "cardio", roomId: "cardio",
      purpose: "Controlled running — base miles, intervals and sprint finishes, weather-proof.",
      brand: "TBC", specs: [["Units", "TBC"], ["Classes", "Engine Room sessions"]], photo: null },
    { id: "rower", name: "Rowing ergs", category: "cardio", roomId: "cardio",
      purpose: "Full-body low-impact engine work — legs, hips, back, arms in one stroke.",
      brand: "TBC", specs: [["Units", "TBC"]], photo: null },
    { id: "ski", name: "Ski ergs", category: "cardio", roomId: "cardio",
      purpose: "Standing pull-based cardio — a favourite in HYROX programming.",
      brand: "TBC", specs: [["Units", "TBC"]], photo: null },
    { id: "bike", name: "Bikes", category: "cardio", roomId: "cardio",
      purpose: "Low-impact intervals and warm-ups — easy on the knees, brutal on the lungs when asked.",
      brand: "TBC", specs: [["Units", "TBC"]], photo: null },
    { id: "yoga", name: "Yoga props", category: "studio", roomId: "studio",
      purpose: "Blocks, straps and mats so every body finds the pose, not the other way round.",
      brand: "TBC", specs: [["Provided", "Mats provided — confirm"]], photo: null },
    { id: "av", name: "Studio sound & lights", category: "studio", roomId: "studio",
      purpose: "The club-light system that turns a Tuesday into a music video.",
      brand: "TBC", specs: [], photo: null },
    { id: "plunge", name: "Cold plunge", category: "recovery", roomId: "recovery",
      purpose: "Cold-water immersion for recovery — guided three-minute protocols, coached breathing.",
      brand: "TBC", specs: [["Temperature", "TBC"], ["Booking", "By slot — model TBC"]], photo: { src: "../crops/w301-ice-sq.jpg", alt: "Cold plunge with ice — art direction" } },
    { id: "steam", name: "Steam room", category: "recovery", roomId: "recovery",
      purpose: "Warm humid heat to unwind after training — pair it with the plunge if you dare.",
      brand: "TBC", specs: [["Capacity", "TBC"]], photo: null }
  ];

  /* ---- batches: weekly recurring (days are 3-letter) — ONE source for
         flap board, timetable and room details ----
         coach/level marked TBC where unconfirmed. durations in minutes. */
  const batches = [
    { id: "b1",  name: "Barbell Club", category: "strength", roomId: "strength", time: "06:00", duration: 60, coach: "TBC", level: "All levels", days: ["mon","wed","fri"],
      desc: "Coached barbell progressions from first pull to working sets. Chalk provided, egos are not.", bring: "Flat shoes, water, a beginner's mind." },
    { id: "b2",  name: "Express Engine", category: "cardio", roomId: "cardio", time: "12:15", duration: 45, coach: "TBC", level: "All levels", days: ["mon"],
      desc: "Lunchtime ergs, skis and sleds. In, loud, out.", bring: "Towel, water." },
    { id: "b3",  name: "Functional Circuits", category: "hybrid", roomId: "hybrid", time: "17:45", duration: 60, coach: "TBC", level: "All levels", days: ["mon"],
      desc: "Carries, ropes and boxes on the turf — a full-body tour of the fun equipment.", bring: "Trainers you trust." },
    { id: "b4",  name: "Cold Open", category: "recovery", roomId: "recovery", time: "20:00", duration: 45, coach: "TBC", level: "All levels", days: ["mon","wed"],
      desc: "Guided cold-plunge immersion with breathing coaching, steam after. Excuses checked at the door.", bring: "Swimwear, towel." },
    { id: "b5",  name: "Dawn Engine", category: "cardio", roomId: "cardio", time: "07:00", duration: 60, coach: "TBC", level: "Intermediate", days: ["tue"],
      desc: "Zone-2 builds with sprint finishes. HYROX candidates welcome; coffee after, mandatory.", bring: "Water, patience for the last interval." },
    { id: "b6",  name: "HYROX Prep", category: "hybrid", roomId: "hybrid", time: "19:00", duration: 75, coach: "TBC", level: "All levels", days: ["tue","thu"],
      desc: "Race-station circuits — run, pull, push, wall. Scaled for first-timers, sharpened for racers.", bring: "Trainers, water, small towel." },
    { id: "b7",  name: "Zumba Nights", category: "studio", roomId: "studio", time: "19:30", duration: 60, coach: "TBC", level: "All levels", days: ["tue"],
      desc: "Club lights, full choreography, zero mirrors. The warm-up is a song you know.", bring: "Your friend who 'doesn't do gyms'." },
    { id: "b8",  name: "Barbell Club II", category: "strength", roomId: "strength", time: "18:00", duration: 60, coach: "TBC", level: "All levels", days: ["tue"],
      desc: "Pull day, programmed. Progress logged on the house board.", bring: "Flat shoes, water." },
    { id: "b9",  name: "Threshold", category: "cardio", roomId: "cardio", time: "07:00", duration: 60, coach: "TBC", level: "Intermediate", days: ["thu"],
      desc: "Threshold intervals on erg and treadmill. The screens play; you supply the plot.", bring: "Water, towel." },
    { id: "b10", name: "Yoga Flow", category: "studio", roomId: "studio", time: "19:45", duration: 60, coach: "TBC", level: "All levels", days: ["thu"],
      desc: "Slow flow under dimmed studio light — the one class where loud is optional.", bring: "Nothing. Mats and props provided." },
    { id: "b11", name: "Barbell Club III", category: "strength", roomId: "strength", time: "06:00", duration: 60, coach: "TBC", level: "All levels", days: ["fri"],
      desc: "Full-body strength finishers. The week ends the way it started: heavy.", bring: "Flat shoes, water." },
    { id: "b12", name: "Dance Floor Theory", category: "studio", roomId: "studio", time: "19:30", duration: 75, coach: "TBC", level: "All levels", days: ["fri"],
      desc: "The flagship. Choreography, club lights, and the last song nobody skips.", bring: "Energy. That's it." },
    { id: "b13", name: "HYROX Simulation", category: "hybrid", roomId: "hybrid", time: "09:00", duration: 90, coach: "TBC", level: "Intermediate", days: ["sat"],
      desc: "Full race-simulation stations on the turf. Run the race before the race.", bring: "Race kit, water, electrolytes." },
    { id: "b14", name: "Cold & Slow", category: "recovery", roomId: "recovery", time: "11:00", duration: 60, coach: "TBC", level: "All levels", days: ["sat"],
      desc: "Open plunge and long steam. Sunday's proving ground.", bring: "Swimwear, towel." },
    { id: "b15", name: "Sunrise Yoga", category: "studio", roomId: "studio", time: "08:00", duration: 60, coach: "TBC", level: "All levels", days: ["sun"],
      desc: "Gentle flow to open the week — breath first, espresso after.", bring: "Nothing. Props provided." },
    { id: "b16", name: "Long Slow Coffee", category: "community", roomId: "lounge", time: "10:00", duration: 90, coach: "—", level: "Everyone", days: ["sun"],
      desc: "No coach, no clock. Read the paper, argue about training, stay for refills.", bring: "Opinions." },
    { id: "b17", name: "Open Floor", category: "community", roomId: "strength", time: "16:00", duration: 120, coach: "—", level: "Everyone", days: ["sun"],
      desc: "The building, empty-ish. Move whatever way the week didn't let you.", bring: "Whatever you train in." }
  ];

  /* ---- events: one-off, sample dates for review ---- */
  const events = [
    { id: "e1", name: "Neon Dance Night", category: "studio", roomId: "studio", date: "2026-10-02", day: "fri", time: "20:00", duration: 90, coach: "TBC", level: "Everyone",
      desc: "A one-off open-floor dance session under full club lights — the studio's loudest hour of the month.", bring: "Energy and a friend." },
    { id: "e2", name: "HYROX Simulation Day", category: "hybrid", roomId: "hybrid", date: "2026-10-10", day: "sat", time: "09:00", duration: 150, coach: "TBC", level: "Intermediate",
      desc: "A full run-through of the race format with timed stations. Scaling options for first-timers.", bring: "Race kit, water, electrolytes." },
    { id: "e3", name: "Cold Plunge Workshop", category: "recovery", roomId: "recovery", date: "2026-10-17", day: "sat", time: "11:00", duration: 75, coach: "TBC", level: "All levels",
      desc: "Breathing coaching, plunge protocols and the science of the shiver — guided end to end.", bring: "Swimwear, two towels, warm layer." },
    { id: "e4", name: "Community Lift", category: "community", roomId: "strength", date: "2026-09-26", day: "sat", time: "10:00", duration: 120, coach: "TBC", level: "Everyone",
      desc: "Open strength floor with coaches on hand — bring a friend, they train free this day. (TBC)", bring: "Normal kit." },
    { id: "e5", name: "Open House Tours", category: "community", roomId: "lobby", date: "2026-10-24", day: "sat", time: "12:00", duration: 180, coach: "—", level: "Everyone",
      desc: "Walk the whole floor with a coach, see every room, ask everything. Trials bookable on the day.", bring: "Curiosity." }
  ];

  /* ---- memberships: structure only — NO invented prices ---- */
  const memberships = [
    { id: "m1", name: "Training Pass — Monthly", billing: "per month", duration: "Rolling monthly", price: null,
      highlight: false, samplePriceNote: true,
      included: ["All training zones", "All weekly batches", "Lounge access", "Member parking — to confirm"],
      classes: "All recurring batches included",
      extras: ["Recovery bookings — model TBC", "Guest passes — TBC"],
      terms: [["Joining fee", "TBC"], ["Cancellation", "TBC"], ["Freeze / pause", "TBC"]] },
    { id: "m2", name: "Training Pass — Annual", billing: "per year", duration: "12 months", price: null,
      highlight: true, highlightNote: "Proposed house pick — awaiting owner confirmation", samplePriceNote: true,
      included: ["All training zones", "All weekly batches", "Lounge access", "Member parking — to confirm", "Priority event booking — TBC"],
      classes: "All recurring batches included",
      extras: ["Recovery bookings — model TBC", "Guest passes — TBC"],
      terms: [["Joining fee", "TBC"], ["Cancellation", "TBC — annual terms"], ["Freeze / pause", "TBC"]] },
    { id: "m3", name: "Off-Peak Pass", billing: "per month", duration: "Rolling monthly", price: null,
      highlight: false, samplePriceNote: true,
      included: ["All zones — off-peak hours", "Off-peak batches", "Lounge access"],
      classes: "Batches starting before 16:00 — definition TBC",
      extras: ["Recovery bookings — model TBC"],
      terms: [["Joining fee", "TBC"], ["Cancellation", "TBC"], ["Freeze / pause", "TBC"]] }
  ];

  /* ---- contact: EVERY value sample until the owner confirms ---- */
  const contact = {
    sampleNotice: "Prototype — the details below are placeholders. Real address, hours and numbers are pending owner confirmation.",
    address: ["Unit / street — TBC", "City — TBC"],
    hours: [["Mon – Fri", "05:30 – 23:00 ◇"], ["Sat – Sun", "07:00 – 21:00 ◇"]],
    phone: "+00 000 000 0000 ◇",
    whatsapp: "+00 000 000 0000 ◇",
    email: "hello@coreculture.example ◇",
    directions: "#" ,
    socials: [["Instagram", "#"], ["Facebook", "#"], ["TikTok", "#"]],
    parking: "On-site member parking — brand promise confirmed in concept copy; count and terms TBC.",
    access: "Step-free access — to confirm."
  };

  const profile = {
    name: "Core Culture",
    tagline: "This is your Training Ground",
    motto: "Train · Move · Recover · Connect",
    hoursShort: "Hours ◇ 05:30–23:00 · 7 days",
    hero: { src: "../crops/w301-hero-dance.jpg", alt: "Dancer in silhouette between pink neon tubes — Core Culture brand art direction" },
    imageryNotice: "Photographs are brand art direction from the concept work — not yet verified photography of the actual gym."
  };

  return { categories, rooms, equipment, batches, events, memberships, contact, profile };
})();
