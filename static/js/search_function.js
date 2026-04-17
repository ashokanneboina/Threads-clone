const input = document.getElementById("searchInput");
const results = document.getElementById("results");

let timeout = null;

input.addEventListener("keyup", function () {
    clearTimeout(timeout);
    
    timeout = setTimeout(() => {
        const query = input.value;
        fetch(`/search/?q=${query}`, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
            .then(res => res.text())
            .then(data => {
                results.innerHTML = "";
                results.innerHTML = data;
            });
    }, 300);
});
