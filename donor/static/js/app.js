// ==========================
// app.cleaned.js — Full JS (Cleaned, WebSocket removed)
// Preserves: GSAP/Locomotive, FAQ toggle, Notifications, Contact form,
// Chat modal (AJAX polling), user list, contact save, and other features.
// WebSocket-related code REMOVED to stop `WebSocket not connected` errors.
// ==========================

document.addEventListener("DOMContentLoaded", function () {
  // --------------------------
  // GSAP + Locomotive Scroll Setup
  // --------------------------
  try {
    gsap.registerPlugin(ScrollTrigger);

    const locoScrollEl = document.querySelector(".main");
    if (locoScrollEl) {
      const locoScroll = new LocomotiveScroll({
        el: locoScrollEl,
        smooth: true,
      });

      locoScroll.on("scroll", ScrollTrigger.update);

      ScrollTrigger.scrollerProxy(".main", {
        scrollTop(value) {
          return arguments.length
            ? locoScroll.scrollTo(value, 0, 0)
            : locoScroll.scroll.instance.scroll.y;
        },
        getBoundingClientRect() {
          return {
            top: 0,
            left: 0,
            width: window.innerWidth,
            height: window.innerHeight,
          };
        },
        pinType: document.querySelector(".main").style.transform ? "transform" : "fixed",
      });

      ScrollTrigger.addEventListener("refresh", () => locoScroll.update());
      ScrollTrigger.refresh();

      window.addEventListener("load", () => {
        locoScroll.update();
        ScrollTrigger.refresh();
      });
    }

    if (document.querySelector(".hero-content")) {
      gsap.from(".hero-content", {
        y: 100,
        duration: 0.6,
        ease: "power1.inOut",
        delay: 2.2,
        opacity: 0,
      });
    }
  } catch (err) {
    console.warn("GSAP/Locomotive init error:", err);
  }

  // --------------------------
  // FAQ Toggle
  // --------------------------
  (function initFaq() {
    try {
      const openId = localStorage.getItem("openFaqId");
      if (openId) {
        const $item = $(`.faq-item[data-id="${openId}"]`);
        $item.addClass("active");
        $item.find(".faq-answer").slideDown();
      }

      $(document).on("click", ".faq-question", function () {
        const $item = $(this).closest(".faq-item");
        $(".faq-item").not($item).removeClass("active").find(".faq-answer").slideUp();
        $item.toggleClass("active");
        $item.find(".faq-answer").slideToggle();

        if ($item.hasClass("active")) {
          localStorage.setItem("openFaqId", $item.data("id"));
        } else {
          localStorage.removeItem("openFaqId");
        }
      });
    } catch (e) {
      console.warn("FAQ init error:", e);
    }
  })();

  // --------------------------
  // Notification System
  // --------------------------
  (function initNotifications() {
    const notifBtn = document.getElementById("notification-btn");
    const notifModal = document.getElementById("notification-modal");
    const notifList = document.getElementById("notification-list");
    const notifCount = document.getElementById("notif-count");

    if (!notifBtn || !notifModal || !notifList || !notifCount) return;

    function updateNotifCount() {
      fetch(window.NOTIF_URL || "/get-notifications/")
        .then((res) => res.json())
        .then((data) => {
          if (data.count > 0) {
            notifCount.style.display = "inline-block";
            notifCount.innerText = data.count;
          } else {
            notifCount.style.display = "none";
          }
        })
        .catch((err) => console.error("Notif count error:", err));
    }

    updateNotifCount();
    setInterval(updateNotifCount, 5000);

    notifBtn.addEventListener("click", () => {
      if (window.IS_AUTHENTICATED === "false") {
        window.location.href = window.LOGIN_URL;
        return;
      }

      const isVisible = notifModal.style.display === "block";
      notifModal.style.display = isVisible ? "none" : "block";

      if (!isVisible) {
        fetch(window.NOTIF_URL || "/get-notifications/")
          .then((res) => res.json())
          .then((data) => {
            notifList.innerHTML = "";
            if (!data.notifications || data.notifications.length === 0) {
              notifList.innerHTML = "<p>You don't have any notification.</p>";
            } else {
              data.notifications.forEach((n) => {
                const div = document.createElement("div");
                div.className = `notif-item ${n.is_read ? "" : "unread-notif"}`;
                div.style.paddingLeft = "10px";
                div.style.borderBottom = "1px solid #ddd";
                div.innerHTML = `<p style='color:#fff; '>${n.message}</p><small style='color:#fff;'>${n.created_at}</small><br>${
                  n.link ? `<a style='color:red; font-family:poppins;' href='${n.link}'>View</a>` : ""
                }`;
                notifList.appendChild(div);
              });
            }

            fetch(window.MARK_NOTIF_URL || "/mark-notifications-read/")
              .then(() => {
                notifCount.style.display = "none";
              })
              .catch((err) => console.error("Mark notif read error:", err));
          })
          .catch((err) => console.error("Fetch notifications error:", err));
      }
    });
  })();

  // --------------------------
  // Contact Form Submit (AJAX)
  // --------------------------
  (function initContactForm() {
    const contactForm = document.getElementById("contactForm");
    if (!contactForm) return;

    contactForm.addEventListener("submit", function (e) {
      e.preventDefault();
      let formData = new FormData(this);
      let button = this.querySelector("button");

      fetch(window.location.origin + "/save-contact/", {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
      })
        .then((res) => res.json())
        .then((data) => {
          let msg = document.getElementById("formMessage");
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
        })
        .catch((err) => console.error("Contact send error:", err));
    });
  })();

  // --------------------------
  // Chat System (AJAX Polling)
  // --------------------------
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

    function loadUsers() {
      fetch("/chat/users/")
        .then((res) => res.json())
        .then((data) => {
          if (!userListEl) return;
          userListEl.innerHTML = "";
          data.users.forEach((u) => {
            const li = document.createElement("li");
            li.textContent = u.username;
            li.style.padding = "6px";
            li.style.cursor = "pointer";
            li.dataset.userid = u.id;
            li.addEventListener("click", () => openChat(u.id, u.username));
            userListEl.appendChild(li);
          });
        })
        .catch((err) => console.error("Load users error:", err));
    }

    function openChat(userId, username) {
      activeChatUserId = userId;
      lastMessageId = 0;
      if (chatHeader) chatHeader.textContent = username ? `Chat with ${username}` : "Chat";
      if (chatHistoryEl) chatHistoryEl.innerHTML = "<p style='opacity:.6'>Loading...</p>";

      fetch(`/chat/history/${userId}/`)
        .then((res) => res.json())
        .then((data) => {
          if (!chatHistoryEl) return;
          chatHistoryEl.innerHTML = "";
          data.messages.forEach((m) => renderMessage(m));
          if (data.messages.length > 0) {
            lastMessageId = data.messages[data.messages.length - 1].id;
          }
          scrollChatToBottom();
        })
        .catch((err) => console.error("Load history error:", err));

      if (pollInterval) clearInterval(pollInterval);

      pollInterval = setInterval(() => {
        if (!activeChatUserId) return;
        fetch(`/chat/poll/${userId}/?last_id=${lastMessageId}`)
          .then((res) => res.json())
          .then((data) => {
            data.messages.forEach((m) => {
              renderMessage(m);
              lastMessageId = m.id;
            });
            if (data.messages.length > 0) scrollChatToBottom();
          })
          .catch((err) => console.error("Poll messages error:", err));
      }, POLL_MS);
    }

function renderMessage(m) {
  if (!chatHistoryEl) return;
  const div = document.createElement("div");
  div.classList.add("chat-message");

  const isMine = Number(m.sender_id) === Number(window.USER_ID);

  if (isMine) {
    div.classList.add("chat-my-message");
    div.innerHTML = `
      <div class="bubble my-bubble">
        <span class="sender">You</span>
        <p>${escapeHtml(m.message)}</p>
      </div>
    `;
  } else {
    div.classList.add("chat-other-message");
    div.innerHTML = `
      <div class="bubble other-bubble">
        <span class="sender">${m.sender_username || "Unknown"}</span>
        <p>${escapeHtml(m.message)}</p>
      </div>
    `;
  }

  chatHistoryEl.appendChild(div);
}
    function scrollChatToBottom() {
      if (!chatHistoryEl) return;
      chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
    }

    if (chatForm) {
      chatForm.addEventListener("submit", function (e) {
        e.preventDefault();
        if (!activeChatUserId) return alert("Select a user first.");
        const msg = chatInput ? chatInput.value.trim() : "";
        if (!msg) return;

        const formData = new FormData();
        formData.append("message", msg);

        fetch(`/chat/send/${activeChatUserId}/`, {
          method: "POST",
          body: formData,
          headers: {"X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value}
        })
        .then(res => {
          if (!res.ok) {
            return res.json().then(err => { throw err });
          }
          return res.json();
        })
        .then(m => {
          renderMessage(m);
          lastMessageId = m.id;
          if (chatInput) chatInput.value = "";
          scrollChatToBottom();
        })
        .catch(err => {
          alert(err.error || "Failed to send message. Try again.");
        });
      });
    }

    chatBtn.addEventListener("click", function () {
      chatModal.style.display = chatModal.style.display === "block" ? "none" : "block";
      if (chatModal.style.display === "block") {
        loadUsers();
      } else {
        if (pollInterval) { clearInterval(pollInterval); pollInterval = null; }
      }
    });

    window.selectUser = function (user) {
      openChat(user.id, user.username);
    };

    function escapeHtml(unsafe) {
      return unsafe
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }
  })();
window.openChat = openChat;
  // --------------------------
  // User List Loader
  // --------------------------
  (function initUserListOnLoad() {
    try {
      if (document.getElementById("user-list")) {
        fetch("/get-users/")
          .then((res) => res.json())
          .then((data) => {
            let userList = document.getElementById("user-list");
            if (!userList) return;
            userList.innerHTML = "";
            data.users.forEach((u) => {
              let li = document.createElement("li");
              li.textContent = u.username;
              li.style.cursor = "pointer";
              li.dataset.userid = u.id;
              li.onclick = () => window.selectUser ? window.selectUser(u) : null;
              userList.appendChild(li);
            });
          })
          .catch((err) => console.warn("get-users error:", err));
      }
    } catch (e) {
      console.warn("initUserListOnLoad error:", e);
    }
  })();
});

function updateUnreadBadge() {
  fetch("/chat/unread_count/")
    .then(res => res.json())
    .then(data => {
      const count = data.unread_count || 0;
      const badge = document.getElementById("chat-unread");
      if (!badge) return;
      if (count > 0) {
        badge.style.display = "inline-block";
        badge.innerText = count;
      } else {
        badge.style.display = "none";
      }
    })
    .catch(err => console.error("Error loading unread count:", err));
}

// call on page load
document.addEventListener("DOMContentLoaded", updateUnreadBadge);

// also call periodically, e.g., every 5 sec
setInterval(updateUnreadBadge, 5000);