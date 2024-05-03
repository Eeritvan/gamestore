window.addEventListener("load", (event) => {
    var links = [
        { class: "home-icon", icon: "home" },
        { class: "search-icon", icon: "search" },
        { class: "library-icon", icon: "joystick" },
        { class: "wishlist-icon", icon: "favorite" },
        { class: "cart-icon", icon: "shopping_cart" },
        { class: "balance-icon", icon: "payments" },
        { class: "wallet-icon", icon: "wallet" },
        { class: "pay-icon", icon: "account_balance_wallet" },
        { class: "cart_off-icon", icon: "shopping_cart_off" },
        { class: "delete-icon", icon: "delete" },
        { class: "clear-icon", icon: "close" },
        { class: "unwish-icon", icon: "heart_broken" },
        { class: "heart-icon", icon: "favorite" },
        { class: "alreadywished-icon", icon: "heart_check" },
        { class: "check-icon", icon: "check" },
        { class: "addcart-icon", icon: "shopping_cart_checkout" },
        { class: "incart-icon", icon: "production_quantity_limits" },
        { class: "schedule-icon", icon: "schedule" },
        { class: "next-icon", icon: "chevron_right" },
        { class: "edit-icon", icon: "edit" },
        { class: "history-icon", icon: "history" },
        { class: "login-icon", icon: "login" },
    ];

    links.forEach(function(link) {
        var linkElements = document.getElementsByClassName(link.class);
        Array.from(linkElements).forEach(function(linkElement) {
            var icon = document.createElement("span");
            icon.className = "material-symbols-rounded";
            icon.textContent = link.icon;
            linkElement.prepend(icon);
        });
    });
});