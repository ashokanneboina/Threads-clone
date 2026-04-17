document.addEventListener("DOMContentLoaded", () => {
    
    if (!isAuthenticated) {
        return;  
    }
    const openBtn = document.getElementById("openModal");
    const closeBtn = document.getElementById("closeModal");
    const modal = document.getElementById("modal");
    const overlay = document.getElementById("overlay");
    
    const postBtn = document.getElementById("postBtn");
    const text = document.getElementById("threadText");
    const image = document.getElementById("threadImage");
    
    console.log(text.value);
    openBtn.addEventListener("click", (e) => {
        e.preventDefault();
        modal.classList.remove("hidden");
        overlay.classList.remove("hidden");
        
        text.focus();
    });
    
    closeBtn.addEventListener("click", () => {
        modal.classList.add("hidden");
        overlay.classList.add("hidden");
    });
    
    postBtn.addEventListener("click", () => {
        const content = text.value.trim();
        const file = image.files[0];
        
        if (!content && !file) {
            alert("Write something or add an image");
            return;
        }
        const formData = new FormData();
        formData.append("content", content);
        
        if (file) {
            formData.append("image", file);
        }
        
        fetch("/create-thread/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    text.value = "";
                    image.value = "";
                    
                    modal.classList.add("hidden");
                    overlay.classList.add("hidden");
                }
                else {
                    alert("error posting thread");
                }
            })
            .catch(err => {
                console.error(err);
            });
    });
});

function getCookie() {
    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken'))
        ?.split('=')[1];
}