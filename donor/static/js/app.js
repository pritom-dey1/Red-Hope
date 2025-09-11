

document.addEventListener("DOMContentLoaded", function () {
  // ==========================
  // GSAP + Locomotive Scroll Setup
  // ==========================
  try {
    gsap.registerPlugin(ScrollTrigger);

    const locoScrollEl = document.querySelector(".main");
    if (locoScrollEl) {
      const locoScroll = new LocomotiveScroll({ el: locoScrollEl, smooth: true });

      locoScroll.on("scroll", ScrollTrigger.update);

      ScrollTrigger.scrollerProxy(".main", {
        scrollTop(value) {
          return arguments.length
            ? locoScroll.scrollTo(value, 0, 0)
            : locoScroll.scroll.instance.scroll.y;
        },
        getBoundingClientRect() {
          return { top: 0, left: 0, width: window.innerWidth, height: window.innerHeight };
        },
        pinType: locoScrollEl.style.transform ? "transform" : "fixed",
      });

      ScrollTrigger.addEventListener("refresh", () => locoScroll.update());
      ScrollTrigger.refresh();

      window.addEventListener("load", () => {
        locoScroll.update();
        ScrollTrigger.refresh();
      });
    }

    const heroContent = document.querySelector(".hero-content");
    if (heroContent) {
      gsap.from(heroContent, { y: 100, duration: 0.6, ease: "power1.inOut", opacity: 0 });
      
   
    }
  } catch (err) {
    console.warn("GSAP/Locomotive init error:", err);
  }

  // ==========================
  // FAQ Toggle (Plain JS)
  // ==========================
  (function initFaq() {
    try {
      const openId = localStorage.getItem("openFaqId");
      if (openId) {
        const item = document.querySelector(`.faq-item[data-id="${openId}"]`);
        if (item) {
          item.classList.add("active");
          const answer = item.querySelector(".faq-answer");
          if (answer) answer.style.display = "block";
        }
      }

      document.addEventListener("click", (e) => {
        if (!e.target.matches(".faq-question")) return;
        const item = e.target.closest(".faq-item");
        if (!item) return;

        document.querySelectorAll(".faq-item").forEach((el) => {
          if (el !== item) {
            el.classList.remove("active");
            const ans = el.querySelector(".faq-answer");
            if (ans) ans.style.display = "none";
          }
        });

        const answer = item.querySelector(".faq-answer");
        const isActive = item.classList.toggle("active");
        if (answer) answer.style.display = isActive ? "block" : "none";

        if (isActive) localStorage.setItem("openFaqId", item.dataset.id);
        else localStorage.removeItem("openFaqId");
      });
    } catch (e) {
      console.warn("FAQ init error:", e);
    }
  })();

  // ==========================
  // Notification System
  // ==========================
  (function initNotifications() {
    const notifBtn = document.getElementById("notification-btn");
    const notifModal = document.getElementById("notification-modal");
    const notifList = document.getElementById("notification-list");
    const notifCount = document.getElementById("notif-count");
    if (!notifBtn || !notifModal || !notifList || !notifCount) return;

    async function updateNotifCount() {
      try {
        const res = await fetch(window.NOTIF_URL || "/get-notifications/");
        const data = await res.json();
        if (data.count > 0) {
          notifCount.style.display = "inline-block";
          notifCount.innerText = data.count;
        } else notifCount.style.display = "none";
      } catch (err) {
        console.error("Notif count error:", err);
      }
    }

    updateNotifCount();
    setInterval(updateNotifCount, 5000);

    notifBtn.addEventListener("click", async () => {
      if (window.IS_AUTHENTICATED === "false") {
        window.location.href = window.LOGIN_URL;
        return;
      }

      const isVisible = notifModal.style.display === "block";
      notifModal.style.display = isVisible ? "none" : "block";

      if (!isVisible) {
        try {
          const res = await fetch(window.NOTIF_URL || "/get-notifications/");
          const data = await res.json();
          notifList.innerHTML = "";
          if (!data.notifications || data.notifications.length === 0) {
            notifList.innerHTML = "<p>You don't have any notification.</p>";
          } else {
            data.notifications.forEach((n) => {
              const div = document.createElement("div");
              div.className = `notif-item ${n.is_read ? "" : "unread-notif"}`;
              div.style.paddingLeft = "10px";
              div.style.borderBottom = "1px solid #ddd";
              div.innerHTML = `
                <p style='color:#fff;'>${n.message}</p>
                <small style='color:#fff;'>${n.created_at}</small><br>
                ${n.link ? `<a style='color:red; font-family:poppins;' href='${n.link}'>View</a>` : ""}
              `;
              notifList.appendChild(div);
            });
          }
          await fetch(window.MARK_NOTIF_URL || "/mark-notifications-read/");
          notifCount.style.display = "none";
        } catch (err) {
          console.error("Fetch notifications error:", err);
        }
      }
    });
  })();

  // ==========================
  // Contact Form Submit (AJAX)
  // ==========================
  (function initContactForm() {
    const contactForm = document.getElementById("contactForm");
    if (!contactForm) return;

    contactForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const formData = new FormData(this);
      const button = this.querySelector("button");
      try {
        const res = await fetch(window.location.origin + "/save-contact/", {
          method: "POST",
          body: formData,
          headers: { "X-Requested-With": "XMLHttpRequest", "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value },
        });
        const data = await res.json();
        const msg = document.getElementById("formMessage");
        if (data.success) {
          msg.style.color = "green";
          msg.innerText = data.message;
          this.reset();
          if (button) {
            button.innerText = "Sended";
            button.style.backgroundColor = "green";
            setTimeout(() => {
              button.innerText = "Send Now";
              button.style.backgroundColor = "";
            }, 2000);
          }
        } else {
          msg.style.color = "red";
          msg.innerText = data.message || "Error sending message";
        }
      } catch (err) {
        console.error("Contact send error:", err);
      }
    });
  })();

  // ==========================
  // Chat System (AJAX Polling)
  // ==========================
  (function initChatSystem() {
    const chatBtn = document.getElementById("chat-btn");
    const chatModal = document.getElementById("chat-modal");
    const userListEl = document.getElementById("user-list");
    const chatHistoryEl = document.getElementById("chat-history");
    const chatHeader = document.getElementById("chat-header");
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatUnread = document.getElementById("chat-unread");

    if (!chatBtn || !chatModal) return;

    let activeChatUserId = null;
    let lastMessageId = 0;
    let pollInterval = null;
    const POLL_MS = 3000;

    async function loadUsers() {
      try {
        const res = await fetch("/chat/users/");
        const data = await res.json();
        if (!userListEl) return;
        userListEl.innerHTML = "";
        data.users.forEach((u) => {
          const li = document.createElement("li");
          li.textContent = u.username;
          li.style.cursor = "pointer";
          li.dataset.userid = u.id;
          li.addEventListener("click", () => openChat(u.id, u.username));
          userListEl.appendChild(li);
        });
      } catch (err) {
        console.error("Load users error:", err);
      }
    }

    async function openChat(userId, username) {
      activeChatUserId = userId;
      lastMessageId = 0;
      if (chatHeader) chatHeader.textContent = username ? `Chat with ${username}` : "Chat";
      if (chatHistoryEl) chatHistoryEl.innerHTML = "<p style='opacity:.6'>Loading...</p>";

      try {
        const res = await fetch(`/chat/history/${userId}/`);
        const data = await res.json();
        if (!chatHistoryEl) return;
        chatHistoryEl.innerHTML = "";
        data.messages.forEach((m) => renderMessage(m));
        if (data.messages.length > 0) lastMessageId = data.messages[data.messages.length - 1].id;
        scrollChatToBottom();
      } catch (err) {
        console.error("Load history error:", err);
      }

      if (pollInterval) clearInterval(pollInterval);
      pollInterval = setInterval(async () => {
        if (!activeChatUserId) return;
        try {
          const res = await fetch(`/chat/poll/${userId}/?last_id=${lastMessageId}`);
          const data = await res.json();
          data.messages.forEach((m) => {
            renderMessage(m);
            lastMessageId = m.id;
          });
          if (data.messages.length > 0) scrollChatToBottom();
        } catch (err) {
          console.error("Poll messages error:", err);
        }
      }, POLL_MS);
    }

    function renderMessage(m) {
      if (!chatHistoryEl) return;
      const div = document.createElement("div");
      div.classList.add("chat-message");
      const isMine = Number(m.sender_id) === Number(window.USER_ID);
      div.classList.add(isMine ? "chat-my-message" : "chat-other-message");
      div.innerHTML = `
        <div class="bubble ${isMine ? "my-bubble" : "other-bubble"}">
          <span class="sender">${isMine ? "You" : m.sender_username || "Unknown"}</span>
          <p>${escapeHtml(m.message)}</p>
        </div>
      `;
      chatHistoryEl.appendChild(div);
    }

    function scrollChatToBottom() {
      if (!chatHistoryEl) return;
      chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
    }

    if (chatForm) {
      chatForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        if (!activeChatUserId) return alert("Select a user first.");
        const msg = chatInput.value.trim();
        if (!msg) return;
        const formData = new FormData();
        formData.append("message", msg);
        try {
          const res = await fetch(`/chat/send/${activeChatUserId}/`, {
            method: "POST",
            body: formData,
            headers: { "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value },
          });
          const m = await res.json();
          renderMessage(m);
          lastMessageId = m.id;
          chatInput.value = "";
          scrollChatToBottom();
        } catch (err) {
          alert(err.error || "Failed to send message. Try again.");
        }
      });
    }

    chatBtn.addEventListener("click", () => {
      chatModal.style.display = chatModal.style.display === "block" ? "none" : "block";
      if (chatModal.style.display === "block") loadUsers();
      else if (pollInterval) { clearInterval(pollInterval); pollInterval = null; }
    });

    window.selectUser = openChat;

    function escapeHtml(unsafe) {
      return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }

    window.openChat = openChat;
  })();

  // ==========================
  // User List Loader
  // ==========================
  (function initUserListOnLoad() {
    const userListEl = document.getElementById("user-list");
    if (!userListEl) return;
    fetch("/get-users/")
      .then((res) => res.json())
      .then((data) => {
        userListEl.innerHTML = "";
        data.users.forEach((u) => {
          const li = document.createElement("li");
          li.textContent = u.username;
          li.style.cursor = "pointer";
          li.dataset.userid = u.id;
          li.onclick = () => window.selectUser?.(u);
          userListEl.appendChild(li);
        });
      })
      .catch((err) => console.warn("get-users error:", err));
  })();
});

// ==========================
// Chat Unread Badge Updater
// ==========================
async function updateUnreadBadge() {
  try {
    const res = await fetch("/chat/unread_count/");
    const data = await res.json();
    const count = data.unread_count || 0;
    const badge = document.getElementById("chat-unread");
    if (!badge) return;
    badge.style.display = count > 0 ? "inline-block" : "none";
    badge.innerText = count;
  } catch (err) {
    console.error("Error loading unread count:", err);
  }
}
updateUnreadBadge();
setInterval(updateUnreadBadge, 5000);

// ==========================
// Map Button & Modal Toggle
// ==========================
const mapBtn = document.getElementById("map-btn");
const mapModal = document.getElementById("map-modal");
const mapClose = document.getElementById("map-close");

if (mapBtn) mapBtn.addEventListener("click", () => {
  if (mapModal) mapModal.style.display = "block";
  initLeafletMap();
});
if (mapClose) mapClose.addEventListener("click", () => mapModal && (mapModal.style.display = "none"));

// ==========================
// Leaflet Map Function
// ==========================
let leafletMap;
function initLeafletMap() {
  if (!leafletMap) {
    leafletMap = L.map("map-container").setView([23.8103, 90.4125], 11);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(leafletMap);
  }

  const receiverIcon = L.icon({ iconUrl: "https://cdn-icons-png.flaticon.com/512/3177/3177361.png", iconSize: [35, 35], iconAnchor: [17, 34], popupAnchor: [0, -30] });
  const donorIcon = L.icon({ iconUrl: "https://cdn-icons-png.flaticon.com/512/149/149071.png", iconSize: [35, 35], iconAnchor: [17, 34], popupAnchor: [0, -30] });

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const [userLat, userLng] = [pos.coords.latitude, pos.coords.longitude];
        leafletMap.setView([userLat, userLng], 13);
        L.marker([userLat, userLng], { icon: receiverIcon }).addTo(leafletMap).bindPopup("<b>You are here</b>").openPopup();
        fetch("/donor/donors-json/")
          .then((res) => res.json())
          .then((data) => data.donors.forEach((donor) => L.marker([donor.lat, donor.lng], { icon: donorIcon }).addTo(leafletMap).bindPopup(`<b>${donor.name}</b><br>Blood Group: ${donor.blood_group}`)));
      },
      (err) => console.warn("Geolocation denied:", err)
    );
  }
}

// ==========================
// Mobile Hamburger Menu Toggle
// ==========================
const hamburger = document.querySelector(".hamburger");
const mobileMenu = document.getElementById("mobileMenu");
const closeBtn = document.querySelector(".close-btn");

if (hamburger && mobileMenu) hamburger.addEventListener("click", () => (mobileMenu.style.width = "70%"));
if (closeBtn && mobileMenu) closeBtn.addEventListener("click", () => (mobileMenu.style.width = "0"));


