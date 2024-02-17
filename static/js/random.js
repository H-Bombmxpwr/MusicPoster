//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "Amen_.png",
    "melopobia.png",
    "speak_now.png",
    "free_your_mind.png",
    "gunfighter_ballads.png",
    "texas_hold_em.png",
    "The_2nd_Law.png",
    "Egg_in_the_Backseat.png",
    "acid_rap.png",
    "testing.png",
    "California_.png",
    "traffic.png",
    "RENAISSANCE.png",
    "El_Camino.png",
    "Monkey_Mania.png",
    "new_eyes.png",
    "well_done.png",
    "Promise.png",
    "top_gun.png",
    "I_Never_Loved_a_Man_the_Way_I_Love_You.png",
    "a_lot_about_livin.png",
    "flirtin_with_disiaster.png",
    "the_woman_in_me.png",
    "innerspeaker.png",
    "One_Wayne_G.png",
    "Late_Registration.png",
    "Mandatory_Fun.png",
    "Quaranta.png",
    "Cool_Patrol.png",
    "minute_by_minute.png",
    "an_evening_with_silk_sonic.png",
    "flower_boy.png",
    "cant_buy_a_thrill.png",
    "led_zeppelin_III.png",
    "apolloxxI.png",
    "slippery_when_wet.png",
    "Yours_Dreamily.png",
    "streets_of_bolingbrook.png",
    "pinkerton.png",
    "southern_nights.png",
    "hysteria.png",
    "starboy.png",
    "stick_season.png",
    "red_moon_in_venus.png",
    "The_Beginning.png",
    "mbdtf.png",
    "make_it_big.png",
    "back_in_black.png",
    "once_bitten.png",
    "damn_the_torpedoes.png",
    "astro_lounge.png",
    "son_of_a_son_of_a_sailor.png",
    "they_might_be_giants.png",
    "private_space.png",
    "oxnard.png",
    "very_special_christmas_2.png",
    "off_the_wall.png",
    "desolation_angels.png",
    "american_teen.png",
    "enema_of_the_state.png",
    "Time_Space.png",
    "cage_the_elephant.png",
    "in_utero.png",
    "l-o-v-e.png",
    "1989.png",
    "diver_down.png",
    "sing_the_blues.png",
    "Im_Just_Ken_.png",
    "little_criminals.png",
    "vampires_of_city.png",
    "get_a_grip.png",
    "the_score.png",
    "red.png",
    "thee_sacred_souls.png",
    "han.png",
    "sports.png",
    "thitvs.png",
    "case_study_01.png",
    "rocking_into_the_night.png",
    "cmon.png",
    "pink_friday_2.png",
    "cheryl.png",
    "lover.png",
    "me.png",
    "questions.png",
    "The_College_Dropout.png",
    "system_of_a_down.png",
    "3_feet_high.png",
    "The_Carter_III.png",
    "dr_feel_good.png",
    "uh_huh.png",
    "1988.png",
    "human_after_all.png",
    "melophobia2.png",
    "pimp_a_butterfly.png",
    "MM...FOOD.png",
    "van_halen_II.png",
    "Blood_Sugar_Sex_Magik_.png",
    "rubber_soul.png",
    "channel_orange.png",
    "Brothers.png",
    "best_of_sweet.png",
    "kick.png",
    "yeezus.png",
    "monsters.png",
    "Suddenly_.png",
    "aja.png",
    "Lets_Rock.png",
    "blonde.png",
    "justice.png",
    "erratic_cinema.png"
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
