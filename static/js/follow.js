document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll(".follow-btn")
    
    buttons.forEach(button => {
        button.addEventListener('click', function () {
            const userId = this.dataset.userid;
            const btn = this;
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
                    }
                    else if (data.status === "unfollowed") {
                        btn.innerText = "Follow"
                    }
                    btn.disabled = false;
                    
                })
                .catch(() => {
                    btn.disabled = false;
                    alert("something went wrong");
                });
        });
    });
});

function getCSRFToken() {
    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken'))
        ?.split('=')[1];
}