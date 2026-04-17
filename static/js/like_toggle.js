document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".like-btn").forEach(btn => {

        btn.addEventListener("click", () => {
            const threadId = btn.dataset.id;

            fetch(`/like/${threadId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken()
                }
            })
            .then(res => res.json())
            .then(data => {

                console.log(data); // debug

                const count = btn.querySelector(".like-count");
                const icon = btn.querySelector(".like-icon");

                if (!count || !icon) {
                    console.error("Missing elements");
                    return;
                }

                count.textContent = data.likes_count;

                if (data.status === "liked") {
                    btn.classList.add("liked");
                    icon.src = icon.dataset.liked;
                } else {
                    btn.classList.remove("liked");
                    icon.src = icon.dataset.unliked;
                }

            });

        });

    });

});

function getCSRFToken() {
    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken'))
        ?.split('=')[1];
}