var stars = document.getElementsByClassName("stars")[0]
var icons = document.getElementsByClassName("fa-star")
var vote = 0
var score = document.getElementById("score")
score.innerText = vote
stars.addEventListener("click", function(evt) {
    vote = 0
    for (var i = 0; i < 5; i++) {
        icons[i].style.setProperty("--v", 0)
        if (icons[i] == evt.target) {
            vote = i
            for (var j = 0; j < i; j++) {
                icons[j].style.setProperty("--v", 100)
            }
            var ps = evt.clientX - icons[i].getBoundingClientRect().left
            if (ps / icons[i].offsetWidth < 0.5) {
                icons[i].style.setProperty("--v", 50)
                vote += 0.5
            } else {
                icons[i].style.setProperty("--v", 100)
                vote++
            }
        }
    }
    score.innerText = vote
})