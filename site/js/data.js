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
    strength:  { label: "Strength",  color: "#c95a25", deep: "#8e3e1a" },
    hybrid:    { label: "Hybrid conditioning", color: "#e8ae28", deep: "#a8750e" },
    cardio:    { label: "Cardio & Engine", color: "#c7b09a", deep: "#6e5844" },
    studio:    { label: "Dance · Yoga", color: "#e7dccb", deep: "#8e6d51" },
    recovery:  { label: "Recovery",  color: "#8f9a7a", deep: "#4e5a45" },
    community: { label: "Community", color: "#a99884", deep: "#665342" }
  };

  /* ---- rooms: carousel order = walkthrough order; plan = SVG coords ----
     access: "included" | "bookable" | "tbc"                              */
  const rooms = [
    {
      id: "strength", num: "01", name: "Strength Zone", category: "strength",
      access: "included", accessNote: "Open with every membership — hours to confirm.",
      tagline: "Racks, platforms and iron that means it.",
      intro: "The lifting heart of the club: racks and platforms for barbell work, a machines bay for targeted, biomechanics-backed training.",
      photo: { src: "../assets/images/core-culture-strength-v2.webp", alt: "Female athlete lifting in the Core Culture strength zone — concept photography" },
      amenities: ["Squat racks", "Platforms", "Calibrated plates", "Dumbbells", "Benches"],
      facilities: [
        ["Floor", "Rubber platform flooring"], ["Racks & platforms", "TBC — count to confirm"],
        ["Plates", "Calibrated (kg)"], ["Chalk", "Provided"], ["Coached hours", "See timetable"]
      ],
      plan: { x: 40, y: 40, w: 330, h: 300, letter: "A" },
      gallery: [
        { src: "../assets/images/core-culture-strength-v2.webp", alt: "Female athlete lifting in the strength zone — concept photography", caption: "Strength, kept honest" },
        { src: "../assets/images/core-culture-hero-v2.webp", alt: "Male athlete deadlifting on the Core Culture floor — concept photography", caption: "Iron, kept honest" },
        { src: "../assets/images/core-culture-recovery-v2.webp", alt: "Athletes cooling down inside Core Culture — concept photography", caption: "Work after the work" }
      ],
      equipment: ["rack", "barbell", "plates", "dumbbells", "bench", "cables", "machines"]
    },
    {
      id: "hybrid", num: "02", name: "Hybrid Turf", category: "hybrid",
      access: "included", accessNote: "Open floor; HYROX batches use it on the timetable.",
      tagline: "Sled lanes and a turf track built for HYROX.",
      intro: "A functional floor for sled work, carries, ropes and race simulation — the training ground for HYROX batches and engine days.",
      photo: { src: "../assets/images/core-culture-hero-v2.webp", alt: "Athletes training on an industrial gym floor — concept photography" },
      amenities: ["Sled track", "Turf lane", "Sleds & ropes", "Boxes", "HYROX stations"],
      facilities: [
        ["Surface", "Turf sprint lane"], ["Sleds", "Weighted, lane use"],
        ["HYROX rig", "Stations — layout TBC"], ["Best for", "HYROX prep · circuits · carries"]
      ],
      plan: { x: 390, y: 40, w: 250, h: 300, letter: "C" },
      gallery: [
        { src: "../assets/images/core-culture-hero-v2.webp", alt: "Male athlete driving through a heavy lift — concept photography", caption: "Low and driving" },
        { src: "../assets/images/core-culture-strength-v2.webp", alt: "Female athlete training in the hybrid zone — concept photography", caption: "Grip points, chalk dust" },
        { src: "../assets/images/core-culture-recovery-v2.webp", alt: "Male and female athletes after training — concept photography", caption: "The floor, together" }
      ],
      equipment: ["sled", "ropes", "boxes", "kettlebells", "hyrox"]
    },
    {
      id: "cardio", num: "03", name: "Engine Room", category: "cardio",
      access: "included", accessNote: "Open with every membership; class programming varies.",
      tagline: "Treadmills, ergs and bikes — running, upgraded.",
      intro: "Cardio that doesn't patronise you: platforms for zone-2 base, threshold work and sprint finishes, with screens you're allowed to ignore.",
      photo: { src: "../assets/images/core-culture-hero-v2.webp", alt: "Athlete training under warm industrial lights — concept photography" },
      amenities: ["Treadmills", "Row ergs", "Ski ergs", "Bikes"],
      facilities: [
        ["Machines", "Count & models TBC"], ["Screens", "Training data — optional"],
        ["Programming", "Engine classes on the timetable"], ["Best for", "Base · threshold · HYROX engine"]
      ],
      plan: { x: 660, y: 40, w: 300, h: 130, letter: "D" },
      gallery: [
        { src: "../assets/images/core-culture-hero-v2.webp", alt: "Athlete training under warm industrial lights — concept photography", caption: "Pace, made visible" },
        { src: "../assets/images/core-culture-strength-v2.webp", alt: "Female athlete driving through a lift — concept photography", caption: "Interval lights" }
      ],
      equipment: ["treadmill", "rower", "ski", "bike"]
    },
    {
      id: "studio", num: "04", name: "The Studio", category: "studio",
      access: "included", accessNote: "Included classes; hobby clubs may run as events — see timetable.",
      tagline: "Dance, yoga and hobby clubs under club lights.",
      intro: "A sprung floor with a sound system and zero judgement: dance and zumba evenings, yoga flows, and hobby clubs for people who don't call it cardio.",
      photo: { src: "../assets/images/core-culture-recovery-v2.webp", alt: "Athletes connecting after a session in Core Culture — concept photography" },
      amenities: ["Sprung floor", "Sound system", "Club lights", "Yoga props"],
      facilities: [
        ["Floor", "Sprung — size TBC"], ["Lights", "Programmable studio wash"],
        ["Mirror wall", "TBC — to confirm"], ["Classes", "Dance · zumba · yoga · hobby clubs"]
      ],
      plan: { x: 660, y: 200, w: 300, h: 140, letter: "E" },
      gallery: [
        { src: "../assets/images/core-culture-recovery-v2.webp", alt: "Male and female athletes cooling down together — concept photography", caption: "The last song nobody skips" },
        { src: "../assets/images/core-culture-strength-v2.webp", alt: "Female athlete training under warm light — concept photography", caption: "Club lights, hard work" },
        { src: "../assets/images/core-culture-hero-v2.webp", alt: "Male athlete training on the floor — concept photography", caption: "No spectators" }
      ],
      equipment: ["yoga", "av"]
    },
    {
      id: "recovery", num: "05", name: "Recovery Wing", category: "recovery",
      access: "bookable", accessNote: "Plunge and steam — booking model to confirm (included vs slot-paid).",
      tagline: "Ice bath and steam. Three honest minutes.",
      intro: "Cold plunge and steam for the work after the work. Guided immersion sessions run on the timetable; protocols are coached, not macho.",
      photo: { src: "../assets/images/core-culture-recovery-v2.webp", alt: "Male and female athletes cooling down after training — concept photography" },
      amenities: ["Cold plunge", "Steam", "Towels", "Guided sessions"],
      facilities: [
        ["Plunge", "Temperature TBC — protocol ~3 min"], ["Steam", "Capacity TBC"],
        ["Booking", "By slot — model TBC"], ["Coaching", "Breathing guided in sessions"]
      ],
      plan: { x: 390, y: 360, w: 180, h: 160, letter: "F" },
      gallery: [
        { src: "../assets/images/core-culture-recovery-v2.webp", alt: "Athletes cooling down in the recovery wing — concept photography", caption: "The reset counts" },
        { src: "../assets/images/core-culture-strength-v2.webp", alt: "Female athlete finishing a hard set — concept photography", caption: "Cold, patient" },
        { src: "../assets/images/core-culture-hero-v2.webp", alt: "Male athlete finishing a heavy set — concept photography", caption: "Steam after" }
      ],
      equipment: ["plunge", "steam"]
    },
    {
      id: "lounge", num: "06", name: "The Lounge", category: "community",
      access: "included", accessNote: "Open to members during staffed hours — hours TBC.",
      tagline: "Work-lift balance. Coffee unmetered.",
      intro: "Meetings before the session, people after it. A warm room to work, argue about training and stay longer than you planned.",
      photo: { src: "../assets/images/core-culture-recovery-v2.webp", alt: "Male and female athletes share a post-training moment — concept photography" },
      amenities: ["Seats & desks", "Coffee", "Wi-Fi TBC", "No clocks"],
      facilities: [
        ["Seats", "Count TBC"], ["Coffee", "Included — machine TBC"],
        ["Work setup", "Desks & power — TBC"], ["Vibe", "Sessions end; culture doesn't"]
      ],
      plan: { x: 590, y: 360, w: 370, h: 160, letter: "G" },
      gallery: [
        { src: "../assets/images/core-culture-recovery-v2.webp", alt: "Male and female athletes share a post-training moment — concept photography", caption: "Work-lift balance" },
        { src: "../assets/images/core-culture-strength-v2.webp", alt: "Female athlete in the strength zone — concept photography", caption: "Stay for the people" }
      ],
      equipment: []
    },
    {
      id: "arrival", num: "07", name: "Arrival & Parking", category: "community",
      access: "included", accessNote: "Parking included with membership — to confirm at sign-up.",
      tagline: "Parking. Finally.",
      intro: "Drive in, park without a quest, walk in warm. The lot is part of the membership — arrival should never be the hardest set.",
      photo: { src: "../assets/images/core-culture-hero-v2.webp", alt: "Core Culture training floor at dusk — concept photography" },
      amenities: ["On-site parking", "Step-free entry TBC", "Front desk", "Accessibility TBC"],
      facilities: [
        ["Spaces", "Count TBC — brand promise: plenty"], ["EV charging", "TBC"],
        ["Entry", "Reception & desk"], ["Access", "Step-free route — to confirm"]
      ],
      plan: { strip: true, letter: "P" },
      gallery: [
        { src: "../assets/images/core-culture-hero-v2.webp", alt: "The Core Culture floor in warm evening light — concept photography", caption: "Arrival, un-fought" },
        { src: "../assets/images/core-culture-recovery-v2.webp", alt: "Athletes cooling down together — concept photography", caption: "Walk in warm" }
      ],
      equipment: []
    },
    {
      id: "lobby", num: "00", name: "Lobby & Desk", category: "community",
      access: "included", accessNote: "Front desk during staffed hours.",
      tagline: "Start here. The desk knows your name eventually.",
      intro: "Reception, trial check-ins and the house board. First visit starts with a tour — book one below.",
      photo: { src: "../assets/images/core-culture-strength-v2.webp", alt: "Female athlete arriving on the Core Culture floor — concept photography" },
      amenities: ["Reception", "House board", "Trial check-in"],
      facilities: [
        ["Desk hours", "Staffed hours TBC"], ["Tours", "Bookable with a trial"],
        ["Board", "Personal bests, posted honestly"]
      ],
      plan: { x: 40, y: 360, w: 200, h: 160, letter: "B" },
      gallery: [
        { src: "../assets/images/core-culture-strength-v2.webp", alt: "Female athlete arriving on the Core Culture floor — concept photography", caption: "Start here" }
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

  /* Editorial concept imagery. These are not photographs of a real venue. */
  const art = {
    strength: { src: "assets/images/cc-quietheat-strength-v5.webp", alt: "A mature South Asian woman quietly adjusting a barbell collar in morning light — AI-generated editorial concept photography", heroPosition: "50% 6%" },
    hybrid: { src: "assets/images/cc-quietheat-hybrid-v5.webp", alt: "A Black male athlete training on a rowing machine across a sunlit club floor — AI-generated editorial concept photography", heroPosition: "50% 18%" },
    cardio: { src: "assets/images/cc-quietheat-cardio-v5.webp", alt: "A Latina runner moving through a charcoal club corridor beneath a pool of light — AI-generated editorial concept photography", heroPosition: "50% 15%" },
    studio: { src: "assets/images/cc-quietheat-movement-v5.webp", alt: "An East Asian man performing a controlled rotational movement in a quiet studio — AI-generated editorial concept photography", heroPosition: "50% 12%" },
    recovery: { src: "assets/images/cc-quietheat-recovery-v5.webp", alt: "An East Asian woman cooling down beside a tall window after training — AI-generated editorial concept photography", heroPosition: "50% 10%" },
    lounge: { src: "assets/images/cc-quietheat-community-v5.webp", alt: "Four athletes sharing an unforced conversation at a brushed-steel water point — AI-generated editorial concept photography", heroPosition: "50% 8%" },
    lobby: { src: "assets/images/cc-quietheat-welcome-v5.webp", alt: "A South Asian member receiving a warm welcome at a dark-oak club reception — AI-generated editorial concept photography", heroPosition: "50% 12%" },
    arrival: { src: "assets/images/cc-quietheat-arrival-v5.webp", alt: "A woman in a cobalt coat arriving at the club on a rainy blue-hour morning — AI-generated editorial concept photography", heroPosition: "50% 14%" }
  };
  const roomCopy = {
    strength: ["Build a foundation. Raise your ceiling.", "An illustrative strength-space concept. The exact equipment mix and floor layout will be published only when confirmed."],
    hybrid: ["Strength meets endurance. Find your edge.", "An open-floor conditioning concept for days that bring strength and stamina together. Final equipment and programming remain unconfirmed."],
    cardio: ["Find a pace. Then find your next.", "A conditioning concept for steady work, intervals, and everything in between. The final equipment mix remains unconfirmed."],
    studio: ["Move to your own rhythm.", "A movement concept designed for a different energy and pace. The final class format and room specification remain unconfirmed."],
    recovery: ["The reset is part of the routine.", "A quieter end to the session is part of the concept. The final facilities and format have not yet been confirmed."],
    lounge: ["Good company. A little more time.", "A place to pause and connect is part of the concept. Its final use, services, and access have not yet been confirmed."],
    lobby: ["Your first step into the culture.", "An illustrative welcome concept. Staffing, check-in, and tour arrangements remain unconfirmed."],
    arrival: ["A considered arrival, from the start.", "Explore the arrival concept. Location, access, and any parking information will be published only when confirmed."]
  };
  rooms.forEach(room => {
    [room.tagline, room.intro] = roomCopy[room.id];
    const photo = art[room.id];
    if (photo) {
      room.photo = photo;
      room.gallery = [{ ...photo, caption: room.name + " · AI-generated concept visual" }];
      if (room.id === "strength") room.gallery.push({ ...art.hybrid, caption: "Training in motion · campaign concept" });
      if (room.id === "hybrid") room.gallery.push({ ...art.strength, caption: "Strength in motion · campaign concept" });
    }
  });
  const conceptNames = {
    strength: "Strength Concept",
    hybrid: "Training Floor",
    cardio: "Conditioning Concept",
    studio: "Movement Concept",
    recovery: "Reset Concept",
    lounge: "Community Concept",
    lobby: "Welcome Concept",
    arrival: "Arrival Concept"
  };
  rooms.forEach(room => {
    room.name = conceptNames[room.id];
    if (room.gallery?.[0]) room.gallery[0].caption = `${room.name} · AI-generated concept visual`;
    room.access = "tbc";
    room.accessNote = "Final access details are still to be confirmed.";
    room.amenities = [];
    room.facilities = [];
    room.equipment = [];
  });
  equipment.find(e => e.id === "sled").purpose = "Push or pull a weighted sled to combine strength and conditioning on the turf.";
  equipment.find(e => e.id === "rack").purpose = "Adjustable racks and platforms for squats, presses, and barbell training.";
  equipment.find(e => e.id === "barbell").purpose = "A versatile bar for squats, presses, deadlifts, and coached strength work.";
  equipment.find(e => e.id === "plates").purpose = "Weight plates for measured, incremental loading across barbell exercises.";
  equipment.find(e => e.id === "dumbbells").purpose = "Free weights for controlled strength work, from individual movements to full-body sessions.";
  equipment.find(e => e.id === "machines").purpose = "Guided-resistance machines for focused strength training. Makes and models to be confirmed.";
  equipment.find(e => e.id === "bike").purpose = "Stationary bikes for warm-ups, steady conditioning, and interval sessions.";
  equipment.find(e => e.id === "av").purpose = "Audio and lighting for coached movement classes. Configuration to be confirmed.";
  equipment.find(e => e.id === "plunge").purpose = "A cold-water immersion facility. Availability, guidance, and suitability to be confirmed before use.";
  equipment.find(e => e.id === "steam").purpose = "A warm, humid space to unwind. Access and usage guidance to be confirmed.";
  Object.assign(batches.find(b => b.id === "b4"), {
    name: "Guided Reset",
    desc: "A guided introduction to post-training recovery habits. Session format and suitability guidance are still to be confirmed.",
    bring: "Comfortable training kit."
  });
  Object.assign(batches.find(b => b.id === "b14"), {
    name: "Mobility Reset",
    desc: "An unhurried sample session focused on mobility and downshifting after training. Final programming is still to be confirmed.",
    bring: "Comfortable training kit."
  });
  Object.assign(events.find(e => e.id === "e3"), {
    name: "Recovery Workshop",
    desc: "A sample workshop on breathing, mobility, and recovery habits. The final format and programming are still to be confirmed.",
    bring: "Comfortable training kit."
  });
  Object.assign(events.find(e => e.id === "e5"), {
    name: "Club Introduction",
    desc: "A sample orientation format for exploring the training concept and asking questions. No event or trial availability is implied.",
    bring: "Questions."
  });
  Object.assign(batches.find(b => b.id === "b6"), {
    name: "Hybrid Circuit",
    desc: "A sample circuit combining strength and conditioning. Final programming and equipment are still to be confirmed."
  });
  Object.assign(batches.find(b => b.id === "b13"), {
    name: "Endurance Simulation",
    desc: "A sample endurance circuit with scalable work blocks. Final programming and equipment are still to be confirmed."
  });
  Object.assign(events.find(e => e.id === "e2"), {
    name: "Endurance Session",
    desc: "A sample endurance session with scalable work blocks. No event availability or specific equipment is implied."
  });
  const sampleSessionCopy = {
    strength: "A sample strength session built around progressive, coached work. Final programming and equipment are still to be confirmed.",
    hybrid: "A sample conditioning session with scalable work blocks. Final programming and equipment are still to be confirmed.",
    cardio: "A sample conditioning session with adjustable intensity. Final programming and equipment are still to be confirmed.",
    studio: "A sample movement session with an adaptable pace. Final programming and room specifications are still to be confirmed.",
    recovery: "A sample post-training reset. Final programming, facilities, and suitability guidance are still to be confirmed.",
    community: "A sample community session format. Final programming, access, and venue details are still to be confirmed."
  };
  batches.forEach(batch => {
    batch.desc = sampleSessionCopy[batch.category];
    batch.bring = batch.category === "community" ? "Questions and curiosity." : "Comfortable training kit and water.";
  });
  Object.assign(batches.find(b => b.id === "b1"), { name: "Strength Foundations" });
  Object.assign(batches.find(b => b.id === "b8"), { name: "Evening Strength" });
  Object.assign(batches.find(b => b.id === "b11"), { name: "Strength Finish" });
  Object.assign(batches.find(b => b.id === "b16"), { name: "Community Reset" });
  Object.assign(batches.find(b => b.id === "b17"), { name: "Open Movement" });
  events.forEach(event => {
    event.desc = sampleSessionCopy[event.category] + " This is an event concept only; no availability is implied.";
    event.bring = event.category === "community" ? "Questions and curiosity." : "Comfortable training kit and water.";
  });
  /* Avoid two sample classes occupying the same strength floor at 06:00 Friday. */
  batches.find(b => b.id === "b1").days = ["mon", "wed"];
  /* The published prototype intentionally exposes no equipment or amenity
     inventory. Keep those details out of the runtime data until confirmed. */
  equipment.splice(0, equipment.length);
  profile.hero = {
    src: "assets/images/cc-nightshift-hero-v3.webp",
    alt: "South Asian woman athlete sprinting through signal-orange light and motion haze — AI-generated campaign photography"
  };
  profile.imageryNotice = "AI-generated concept imagery, not photography of the actual venue.";
  return { categories, rooms, equipment, batches, events, memberships, contact, profile };
})();
