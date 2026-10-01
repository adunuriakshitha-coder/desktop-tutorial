// script.js - fills dropdowns, validates the form and sends it to Flask
const form = document.getElementById("apptForm");
if (form) {
  const dept = document.getElementById("department");
  const doctor = document.getElementById("doctor");

  // Fill the department dropdown with unique departments
  [...new Set(DOCTORS.map(d => d.dept))].forEach(n => dept.add(new Option(n, n)));

  // Show only the doctors of the chosen department
  function fillDoctors(selected) {
    doctor.length = 1;
    DOCTORS.filter(d => d.dept === dept.value).forEach(d => doctor.add(new Option(d.name, d.name)));
    if (selected) doctor.value = selected;
  }
  dept.addEventListener("change", () => fillDoctors());

  // Coming from a doctor card (?doctor=Name)? Pre-select that doctor.
  const chosen = new URLSearchParams(location.search).get("doctor");
  const found = DOCTORS.find(d => d.name === chosen);
  if (found) { dept.value = found.dept; fillDoctors(found.name); }

  const val = id => document.getElementById(id).value.trim();

  function validate() {
    const names = {patient_name:"Patient name", age:"Age", gender:"Gender", phone:"Phone number",
      email:"Email", department:"Department", doctor:"Doctor", appointment_date:"Appointment date",
      appointment_time:"Appointment time", symptoms:"Symptoms"};
    for (const id in names) if (!val(id)) return names[id] + " is required.";
    const age = Number(val("age"));
    if (!Number.isInteger(age) || age < 1 || age > 120) return "Enter a valid age (1-120).";
    if (!/^\d{10}$/.test(val("phone"))) return "Phone number must be exactly 10 digits.";
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(val("email"))) return "Enter a valid email address.";
    const today = new Date(); today.setHours(0, 0, 0, 0);
    if (new Date(val("appointment_date") + "T00:00") < today) return "Appointment date cannot be in the past.";
    return "";
  }

  form.addEventListener("submit", async e => {
    e.preventDefault();
    const error = document.getElementById("error");
    error.textContent = validate();
    if (error.textContent) return;

    const data = {};
    ["patient_name","age","gender","phone","email","department","doctor",
     "appointment_date","appointment_time","symptoms"].forEach(id => data[id] = val(id));

    try {
      const res = await fetch("/book", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(data)});
      const result = await res.json();
      if (!result.success) { error.textContent = result.message; return; }
      const box = document.getElementById("success");
      box.textContent = result.message + " Your Appointment ID is " + result.appointment_id;
      box.hidden = false;
      form.reset(); fillDoctors();
      window.scrollTo({top: 0, behavior: "smooth"});
    } catch (err) {
      error.textContent = "Could not reach the server. Is app.py running?";
    }
  });
}
