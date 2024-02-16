//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "new_eyes.png",
    "off_the_wall.png",
    "cage_the_elephant.png",
    "starboy.png",
    "thee_sacred_souls.png",
    "son_of_a_son_of_a_sailor.png",
    "free_your_mind.png",
    "well_done.png",
    "yeezus.png",
    "cant_buy_a_thrill.png",
    "cmon.png",
    "justice.png",
    "acid_rap.png",
    "rubber_soul.png",
    "enema_of_the_state.png",
    "uh_huh.png",
    "pinkerton.png",
    "melophobia2.png",
    "best_of_sweet.png",
    "once_bitten.png",
    "lover.png",
    "damn_the_torpedoes.png",
    "minute_by_minute.png",
    "gunfighter_ballads.png",
    "the_woman_in_me.png",
    "little_criminals.png",
    "astro_lounge.png",
    "me.png",
    "very_special_christmas_2.png",
    "1989.png",
    "pink_friday_2.png",
    "red.png",
    "rocking_into_the_night.png",
    "traffic.png",
    "sing_the_blues.png",
    "an_evening_with_silk_sonic.png",
    "system_of_a_down.png",
    "3_feet_high.png",
    "vampires_of_city.png",
    "kick.png",
    "Blood_Sugar_Sex_Magik_.png",
    "the_score.png",
    "The_2nd_Law.png",
    "flirtin_with_disiaster.png",
    "erratic_cinema.png",
    "diver_down.png",
    "southern_nights.png",
    "apolloxxI.png",
    "cheryl.png",
    "streets_of_bolingbrook.png",
    "dr_feel_good.png",
    "a_lot_about_livin.png",
    "case_study_01.png",
    "mbdtf.png",
    "they_might_be_giants.png",
    "led_zeppelin_III.png",
    "testing.png",
    "RENAISSANCE.png",
    "The_Beginning.png",
    "american_teen.png",
    "melopobia.png",
    "Mandatory_Fun.png",
    "thitvs.png",
    "slippery_when_wet.png",
    "private_space.png",
    "channel_orange.png",
    "in_utero.png",
    "get_a_grip.png",
    "han.png",
    "make_it_big.png",
    "innerspeaker.png",
    "MM...FOOD.png",
    "pimp_a_butterfly.png",
    "1988.png",
    "l-o-v-e.png",
    "speak_now.png",
    "monsters.png",
    "human_after_all.png",
    "van_halen_II.png",
    "red_moon_in_venus.png",
    "stick_season.png",
    "questions.png",
    "flower_boy.png",
    "Egg_in_the_Backseat.png",
    "oxnard.png",
    "blonde.png",
    "aja.png",
    "desolation_angels.png",
    "texas_hold_em.png",
    "sports.png",
    "back_in_black.png",
    "hysteria.png"
];

    // Function to shuffle an array
    function shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    // Shuffle the posters array
    const shuffledPosters = shuffle(posters);

    // Function to create poster items
    function createPosterItem(src) {
        const posterItem = document.createElement('div');
        posterItem.className = 'poster-item autoscroll';
        const img = document.createElement('img');
        img.src = `static/posters_resized/${src}`;
        img.alt = src;
        posterItem.appendChild(img);
        return posterItem;
    }

    // Append shuffled images to the scroll containers
    const leftContainer = document.querySelector('.poster-scroll-container[style="left: 10px;"]');
    const rightContainer = document.querySelector('.poster-scroll-container[style="right: 10px;"]');

    shuffledPosters.forEach((posterSrc, index) => {
        const posterItem = createPosterItem(posterSrc);
        if (index % 2 === 0) { // Even index, left side
            leftContainer.appendChild(posterItem);
        } else { // Odd index, right side
            rightContainer.appendChild(posterItem);
        }
    });
});
