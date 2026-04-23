document.addEventListener("DOMContentLoaded", function () {

    document.addEventListener("click", function (e) {

        if (!e.target.classList.contains("follow-btn")) return;

        const btn = e.target;
        const userId = btn.dataset.userid;

        if (!userId) return;

        btn.disabled = true;

        fetch("/follow_user/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCSRFToken()
            },
            body: "user_id=" + userId
        })
        .then(res => res.json())
        .then(data => {

            if (data.status === "followed") {
                btn.innerText = "Following";
                btn.classList.add("following");
            }

            else if (data.status === "unfollowed") {
                btn.innerText = "Follow";
                btn.classList.remove("following");
            }

            btn.disabled = false;
        })
        .catch(() => {
            btn.disabled = false;
            alert("Something went wrong");
        });
    });
});


function getCSRFToken() {
    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken'))
        ?.split('=')[1];
}