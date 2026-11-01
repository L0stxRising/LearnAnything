let ev_src = null;
let sel_rt = null;
let v_path = "";
let last_p = "";

// const DEV_SERVER = "http://localhost:8000";
// let current_task_id = null;

const _id = (x) => document.getElementById(x);

/*
function pollStatus(taskId) {
  let timer = setInterval(async () => {
    let r = await fetch("/api/status?id=" + taskId);
    let res = await r.json();
    if (res.completed) {
      clearInterval(timer);
      _id("out_player").src = res.video_url;
    }
  }, 2000);
}
*/

const r_box = _id("rate_btns");
for (let i = 1; i <= 10; i++) {
  let b = document.createElement("button");
  b.type = "button";
  b.className = "star_btn";
  b.innerText = i + " ★";
  b.onclick = function () {
    sel_rt = i;
    document.querySelectorAll(".star_btn").forEach((s) => s.classList.remove("act"));
    b.classList.add("act");
    _id("sub_rate").disabled = false;
  };
  r_box.appendChild(b);
}

function rst() {
  [1, 2, 3].forEach((i) => {
    let el = _id("b" + i);
    el.className = "bdg idle";
    el.innerText = "idle";
  });

  _id("err_bx").style.display = "none";
  _id("vid_wrap").style.display = "none";
  _id("cd_wrap").style.display = "none";
  _id("rt_wrap").style.display = "none";
  _id("sub_rate").disabled = true;
  _id("rt_stat").innerText = "";
  sel_rt = null;

  let v = _id("out_player");
  v.pause();
  v.src = "";
}

function runGen() {
  let txt = _id("in_prompt").value.trim();
  if (!txt) return alert("Please enter a prompt first");

  let inc = _id("chk_inc").checked;
  last_p = txt;
  rst();
  _id("btn_submit").disabled = true;

  if (ev_src) ev_src.close();
  ev_src = new EventSource("/api/render?prompt=" + encodeURIComponent(txt) + "&include_code=" + inc);

  ev_src.onmessage = function (e) {
    try {
      onEv(JSON.parse(e.data));
    } catch (err) {}
  };

  ev_src.onerror = function () {
    if (ev_src) ev_src.close();
    _id("btn_submit").disabled = false;
  };
}

function onEv(d) {
  if (d.type === "stage") {
    let bdg = _id("b" + d.stage);
    if (!bdg) return;
    if (d.status === "processing") {
      bdg.className = "bdg proc";
      bdg.innerText = "processing...";
    } else if (d.status === "done") {
      bdg.className = "bdg done";
      bdg.innerText = "Done";
    } else if (d.status === "error") {
      bdg.className = "bdg err";
      bdg.innerText = "err";
    }
    return;
  }

  if (d.type === "complete") {
    if (ev_src) ev_src.close();
    _id("btn_submit").disabled = false;

    if (d.video_path) {
      v_path = d.video_path;
      _id("vid_wrap").style.display = "block";
      let vp = _id("out_player");
      vp.src = "/api/video?path=" + encodeURIComponent(d.video_path);
      _id("v_info").innerText = "File: " + d.video_path;
      vp.load();
    }

    if (d.code) {
      _id("cd_wrap").style.display = "block";
      _id("raw_code").innerText = d.code;
    }

    _id("rt_wrap").style.display = "block";
    return;
  }

  if (d.type === "error") {
    if (ev_src) ev_src.close();
    _id("btn_submit").disabled = false;
    let er = _id("err_bx");
    er.style.display = "block";
    er.innerText = "Error: " + d.message;
  }
}

async function sendRating() {
  if (!sel_rt) return;
  let st = _id("rt_stat");
  st.innerText = "Saving rating...";

  try {
    let r = await fetch("/api/rate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rating: sel_rt, prompt: last_p, video_path: v_path })
    });
    st.innerText = "Recorded " + sel_rt + "/10. Thank you!";
    _id("sub_rate").disabled = true;
  } catch (err) {
    st.innerText = "Error: " + err.message;
  }
}
