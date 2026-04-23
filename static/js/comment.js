

document.getElementById("comment-form")?.addEventListener("submit", function(e) {
    e.preventDefault();

    const content = this.content.value;

    fetch(window.location.pathname + "comment/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRFToken()
        },
        body: "content=" + content
    })
    .then(() => location.reload());
});


function showReplyBox(commentId) {
    const box = document.getElementById(`reply-box-${commentId}`);

    box.innerHTML = `
        <form onsubmit="submitReply(event, '${commentId}')">
            <input type="text" name="content" placeholder="Reply..." required />
            <button type="submit">Send</button>
        </form>
    `;
}

function submitReply(event, parentId) {
    event.preventDefault();

    const content = event.target.content.value;

    fetch(window.location.pathname + "comment/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRFToken()
        },
        body: "content=" + content + "&parent_id=" + parentId
    })
    .then(() => location.reload());
}


function getCSRFToken() {
    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken'))
        ?.split('=')[1];
}