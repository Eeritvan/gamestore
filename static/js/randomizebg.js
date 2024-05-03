window.onload = function() {
    var animElements = document.querySelectorAll(".anim1, .anim2, .anim3, .anim4, .anim5");
    var colors = [
        "linear-gradient(rgba(42, 232, 153, 0.85), rgba(78, 81, 232, 1))",
        "linear-gradient(to right, #fbd3e9, #bb377d)",
        "linear-gradient(rgba(187, 108, 233, 0.75), rgb(79, 82, 221))",
        "linear-gradient(to right, #4b6cb7, #182848)",
        "linear-gradient(to right, #fbd3e9, #bb377d)"
    ];

    for (let i = colors.length - 1; i > 0; i--) {
        let j = Math.floor(Math.random() * (i + 1));
        [colors[i], colors[j]] = [colors[j], colors[i]];
    }

    animElements.forEach(function(element, index) {
        var randomDelay = Math.random() * -60;

        element.style.animationDelay = randomDelay + "s";
        element.style.backgroundImage = colors[index];
    });

    mediumZoom("img[alt='gameimage']", {
        margin: 100,
        background: "rgba(0, 0, 0, 0.8)",
    });
};