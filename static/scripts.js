function username_api(){
    var request = new XMLHttpRequest()
    request.open('GET', '/get_user_info_api', true)
    request.onload = function () {
        // Begin accessing JSON data here
        var data = JSON.parse(this.response)
        if (request.status >= 200 && request.status < 400) {
            var balance_btn = document.getElementById("navbarDropdownMenuLink");
            balance_btn.innerHTML = data.value;
        } else {
            console.log("Error!!!!!");
        }
    }

    request.send()

}

var favorite = document.querySelector(".custom-checkbox")

favorite.addEventListener("click", {
    if (favo) {
        
    }

})