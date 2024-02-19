//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "led_zeppelin_III.png",
    "One_Wayne_G.png",
    "Berhana.png",
    "monsters.png",
    "justice.png",
    "get_a_grip.png",
    "pink_friday_2.png",
    "uh_huh.png",
    "yeezus.png",
    "1989.png",
    "red.png",
    "GINGER.png",
    "MONTERO.png",
    "Cool_Patrol.png",
    "desolation_angels.png",
    "acid_rap.png",
    "diver_down.png",
    "rubber_soul.png",
    "aja.png",
    "astro_lounge.png",
    "new_eyes.png",
    "Making_Mirrors.png",
    "The_Beginning.png",
    "Vaudeville_Villain.png",
    "3_feet_high.png",
    "well_done.png",
    "The_Carter_III.png",
    "flower_boy.png",
    "questions.png",
    "testing.png",
    "an_evening_with_silk_sonic.png",
    "The_College_Dropout.png",
    "the_woman_in_me.png",
    "Demon_Days.png",
    "Suddenly_.png",
    "California_.png",
    "thitvs.png",
    "Funkentelechy_Vs._The_Placebo_Syndrome.png",
    "case_study_01.png",
    "Blood_Sugar_Sex_Magik_.png",
    "The_2nd_Law.png",
    "red_moon_in_venus.png",
    "Turn_Blue.png",
    "Mandatory_Fun.png",
    "best_of_sweet.png",
    "speak_now.png",
    "erratic_cinema.png",
    "enema_of_the_state.png",
    "free_your_mind.png",
    "Waiting_on_a_Song.png",
    "minute_by_minute.png",
    "starboy.png",
    "they_might_be_giants.png",
    "off_the_wall.png",
    "lover.png",
    "Madman_Across_The_Water.png",
    "I_Never_Loved_a_Man_the_Way_I_Love_You.png",
    "american_teen.png",
    "Monkey_Mania.png",
    "streets_of_bolingbrook.png",
    "very_special_christmas_2.png",
    "the_score.png",
    "Im_Just_Ken_.png",
    "van_halen_II.png",
    "Late_Registration.png",
    "oxnard.png",
    "channel_orange.png",
    "cheryl.png",
    "once_bitten.png",
    "thee_sacred_souls.png",
    "texas_hold_em.png",
    "han.png",
    "hysteria.png",
    "damn_the_torpedoes.png",
    "make_it_big.png",
    "me.png",
    "sports.png",
    "pinkerton.png",
    "RENAISSANCE.png",
    "human_after_all.png",
    "pimp_a_butterfly.png",
    "Egg_in_the_Backseat.png",
    "1988.png",
    "southern_nights.png",
    "flirtin_with_disiaster.png",
    "Amen_.png",
    "sing_the_blues.png",
    "mbdtf.png",
    "WE_ARE_.png",
    "apolloxxI.png",
    "system_of_a_down.png",
    "top_gun.png",
    "melophobia2.png",
    "back_in_black.png",
    "rocking_into_the_night.png",
    "gunfighter_ballads.png",
    "slippery_when_wet.png",
    "cant_buy_a_thrill.png",
    "stick_season.png",
    "Quaranta.png",
    "cmon.png",
    "Rise_And_Fall_Rage_And_Grace.png",
    "son_of_a_son_of_a_sailor.png",
    "Time_Space.png",
    "Honky_Chateau.png",
    "l-o-v-e.png",
    "Brothers.png",
    "a_lot_about_livin.png",
    "Promise.png",
    "vampires_of_city.png",
    "El_Camino.png",
    "dr_feel_good.png",
    "Blue_Moves.png",
    "Ugh_those_feels_again.png",
    "kick.png",
    "traffic.png",
    "blonde.png",
    "Lets_Rock.png",
    "in_utero.png",
    "SOUR.png",
    "MM...FOOD.png",
    "The_Swing.png",
    "cage_the_elephant.png",
    "Yours_Dreamily.png",
    "innerspeaker.png",
    "little_criminals.png",
    "private_space.png"
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
