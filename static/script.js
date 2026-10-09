mdocument.addEventListener("DOMContentLoaded", function () {

    const profilePage = document.querySelector(".profile-page");

    /* =========================================================
       PROFILE PAGE FEATURES
       ========================================================= */

    if (profilePage) {

        /* --------------------
           Scroll Reveal
        -------------------- */

        const revealElements = profilePage.querySelectorAll(".reveal");

        if ("IntersectionObserver" in window) {

            const revealObserver = new IntersectionObserver(
                function (entries, observer) {

                    entries.forEach(function (entry) {

                        if (entry.isIntersecting) {
                            entry.target.classList.add("visible");
                            console.log("Reveal triggered:", entry.target);
                            observer.unobserve(entry.target);
                        }

                    });

                },
                {
                    threshold: 0.12
                }
            );

            revealElements.forEach(function (element) {
                element.classList.add("reveal");
                revealObserver.observe(element);
            });

        } else {

            revealElements.forEach(function (element) {
                element.classList.add("visible");
            });

        }


        /* --------------------
           Active Navigation
        -------------------- */

        const sections = profilePage.querySelectorAll("main section[id]");
        const navLinks = profilePage.querySelectorAll(".main-nav a");

        if ("IntersectionObserver" in window) {

            const sectionObserver = new IntersectionObserver(
                function (entries) {

                    entries.forEach(function (entry) {

                        if (entry.isIntersecting) {

                            const currentId =
                                entry.target.getAttribute("id");

                            navLinks.forEach(function (link) {

                                const linkTarget =
                                    link.getAttribute("href");

                                if (linkTarget === "#" + currentId) {
                                    link.classList.add("active");
                                } else {
                                    link.classList.remove("active");
                                }

                            });

                        }

                    });

                },
                {
                    rootMargin: "-30% 0px -60% 0px"
                }
            );

            sections.forEach(function (section) {
                sectionObserver.observe(section);
            });

        }


        /* --------------------
           Smooth Navigation
        -------------------- */

        navLinks.forEach(function (link) {

            link.addEventListener("click", function (event) {

                const targetId =
                    link.getAttribute("href");

                if (!targetId || !targetId.startsWith("#")) {
                    return;
                }

                const targetElement =
                    profilePage.querySelector(targetId);

                if (!targetElement) {
                    return;
                }

                event.preventDefault();

                targetElement.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            });

        });


        /* --------------------
           Reduced Motion
        -------------------- */

        const reducedMotion = window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        );

        if (reducedMotion.matches) {

            document.documentElement.style.scrollBehavior = "auto";

            revealElements.forEach(function (element) {
                element.classList.add("visible");
            });

        }

    }


    /* =========================================================
       GLOBAL FEATURES
       ========================================================= */

    /* --------------------
       Scroll To Top
       -------------------- */

    const scrollTopButton = document.createElement("button");

    scrollTopButton.type = "button";
    scrollTopButton.className = "scroll-top";
    scrollTopButton.setAttribute(
        "aria-label",
        "Scroll to top"
    );
    scrollTopButton.textContent = "↑";

    document.body.appendChild(scrollTopButton);


    function updateScrollButton() {

        if (window.scrollY > 500) {
            scrollTopButton.classList.add("show");
        } else {
            scrollTopButton.classList.remove("show");
        }

    }


    window.addEventListener(
        "scroll",
        updateScrollButton
    );


    scrollTopButton.addEventListener(
        "click",
        function () {

            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });

        }
    );


    updateScrollButton();

});
