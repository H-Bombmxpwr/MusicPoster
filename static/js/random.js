//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "channel_orange.png",
    "get_a_grip.png",
    "pimp_a_butterfly.png",
    "justice.png",
    "cage_the_elephant.png",
    "The_2nd_Law.png",
    "well_done.png",
    "red_moon_in_venus.png",
    "free_your_mind.png",
    "minute_by_minute.png",
    "slippery_when_wet.png",
    "melopobia.png",
    "very_special_christmas_2.png",
    "astro_lounge.png",
    "little_criminals.png",
    "mbdtf.png",
    "testing.png",
    "new_eyes.png",
    "they_might_be_giants.png",
    "best_of_sweet.png",
    "cant_buy_a_thrill.png",
    "an_evening_with_silk_sonic.png",
    "3_feet_high.png",
    "top_gun.png",
    "oxnard.png",
    "cmon.png",
    "traffic.png",
    "in_utero.png",
    "the_score.png",
    "streets_of_bolingbrook.png",
    "apolloxxI.png",
    "red.png",
    "vampires_of_city.png",
    "han.png",
    "american_teen.png",
    "Mandatory_Fun.png",
    "pinkerton.png",
    "a_lot_about_livin.png",
    "innerspeaker.png",
    "monsters.png",
    "speak_now.png",
    "cheryl.png",
    "damn_the_torpedoes.png",
    "yeezus.png",
    "melophobia2.png",
    "private_space.png",
    "flower_boy.png",
    "rocking_into_the_night.png",
    "desolation_angels.png",
    "l-o-v-e.png",
    "1989.png",
    "system_of_a_down.png",
    "enema_of_the_state.png",
    "uh_huh.png",
    "blonde.png",
    "flirtin_with_disiaster.png",
    "gunfighter_ballads.png",
    "son_of_a_son_of_a_sailor.png",
    "RENAISSANCE.png",
    "off_the_wall.png",
    "kick.png",
    "lover.png",
    "MM...FOOD.png",
    "pink_friday_2.png",
    "thitvs.png",
    "van_halen_II.png",
    "thee_sacred_souls.png",
    "southern_nights.png",
    "me.png",
    "questions.png",
    "dr_feel_good.png",
    "Blood_Sugar_Sex_Magik_.png",
    "make_it_big.png",
    "sports.png",
    "aja.png",
    "1988.png",
    "texas_hold_em.png",
    "sing_the_blues.png",
    "Egg_in_the_Backseat.png",
    "rubber_soul.png",
    "the_woman_in_me.png",
    "back_in_black.png",
    "once_bitten.png",
    "The_Beginning.png",
    "stick_season.png",
    "hysteria.png",
    "case_study_01.png",
    "erratic_cinema.png",
    "led_zeppelin_III.png",
    "starboy.png",
    "human_after_all.png",
    "diver_down.png",
    "acid_rap.png"
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
