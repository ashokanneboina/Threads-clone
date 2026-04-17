document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".save-btn").forEach(btn => {

        btn.addEventListener("click", () => {
            const threadId = btn.dataset.id;

            fetch(`/save/${threadId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken()
                }
            })
            .then(res => res.json())
            .then(data => {

                const icon = btn.querySelector(".save-icon");

                if (data.status === "saved") {
                    btn.classList.add("saved");
                    icon.src = icon.dataset.saved;
                } else {
                    btn.classList.remove("saved");
                    icon.src = icon.dataset.unsaved;
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