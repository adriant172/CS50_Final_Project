function username_api(){
    const request = new XMLHttpRequest()
    request.open('GET', '/get_user_info_api', true)
    request.onload = function () {
        // Begin accessing JSON data here
        const data = JSON.parse(this.response)
        if (request.status >= 200 && request.status < 400) {
            const balance_btn = document.getElementById("navbarDropdownMenuLink");
            balance_btn.innerHTML = data.value;
        } else {
            console.log("Error!!!!!");
        }
    }
    request.send()
}


