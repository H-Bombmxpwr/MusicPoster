//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "son_of_a_son_of_a_sailor.png",
    "The_Life_Of_Pablo.png",
    "never_enough.png",
    "questions.png",
    "get_a_grip.png",
    "Demon_Days.png",
    "enema_of_the_state.png",
    "Lets_Rock.png",
    "thee_sacred_souls.png",
    "gunfighter_ballads.png",
    "I_Never_Loved_a_Man_the_Way_I_Love_You.png",
    "The_Swing.png",
    "make_it_big.png",
    "justice.png",
    "the_score.png",
    "California_.png",
    "RENAISSANCE.png",
    "channel_orange.png",
    "The_Beginning.png",
    "damn_the_torpedoes.png",
    "the_woman_in_me.png",
    "diver_down.png",
    "sing_the_blues.png",
    "Cool_Patrol.png",
    "The_2nd_Law.png",
    "van_halen_II.png",
    "an_evening_with_silk_sonic.png",
    "mbdtf.png",
    "pimp_a_butterfly.png",
    "well_done.png",
    "Mandatory_Fun.png",
    "aja.png",
    "slippery_when_wet.png",
    "l-o-v-e.png",
    "Rise_And_Fall_Rage_And_Grace.png",
    "Egg_in_the_Backseat.png",
    "FALLING_OR_FLYING_.png",
    "system_of_a_down.png",
    "rubber_soul.png",
    "rocking_into_the_night.png",
    "top_gun.png",
    "han.png",
    "red.png",
    "Brothers.png",
    "thitvs.png",
    "new_eyes.png",
    "melophobia2.png",
    "free_your_mind.png",
    "3_feet_high.png",
    "good_kid_maad_city.png",
    "El_Camino.png",
    "be_more.png",
    "cmon.png",
    "Berhana.png",
    "Funkentelechy_Vs._The_Placebo_Syndrome.png",
    "The_Carter_III.png",
    "innerspeaker.png",
    "Promise.png",
    "WE_ARE_.png",
    "apolloxxI.png",
    "lover.png",
    "best_of_sweet.png",
    "SOUR.png",
    "dr_feel_good.png",
    "american_teen.png",
    "ghosts.png",
    "monsters.png",
    "The_College_Dropout.png",
    "traffic.png",
    "a_lot_about_livin.png",
    "GINGER.png",
    "very_special_christmas_2.png",
    "1988.png",
    "private_space.png",
    "Monkey_Mania.png",
    "astro_lounge.png",
    "Time_Space.png",
    "acid_rap.png",
    "One_Wayne_G.png",
    "her_love_still_haunts_me_like_a_ghost.png",
    "led_zeppelin_III.png",
    "pinkerton.png",
    "cheryl.png",
    "Turn_Blue.png",
    "once_bitten.png",
    "speak_now.png",
    "red_moon_in_venus.png",
    "Amen_.png",
    "Vaudeville_Villain.png",
    "erratic_cinema.png",
    "me.png",
    "vampires_of_city.png",
    "Man_On_The_Moon_II__The_Legend_Of_Mr._Rager.png",
    "MONTERO.png",
    "Waiting_on_a_Song.png",
    "feels.png",
    "Im_Just_Ken_.png",
    "uh_huh.png",
    "women_in_music_pt_III.png",
    "Blue_Moves.png",
    "flirtin_with_disiaster.png",
    "Madman_Across_The_Water.png",
    "momints.png",
    "testing.png",
    "KIDS_SEE_GHOSTS.png",
    "Ugh_those_feels_again.png",
    "recess.png",
    "MM...FOOD.png",
    "off_the_wall.png",
    "in_utero.png",
    "oxnard.png",
    "Blood_Sugar_Sex_Magik_.png",
    "human_after_all.png",
    "starboy.png",
    "MANIA.png",
    "Late_Registration.png",
    "blonde.png",
    "streets_of_bolingbrook.png",
    "cage_the_elephant.png",
    "southern_nights.png",
    "hysteria.png",
    "1989.png",
    "Quaranta.png",
    "they_might_be_giants.png",
    "Freudian.png",
    "Yours_Dreamily.png",
    "back_in_black.png",
    "minute_by_minute.png",
    "yeezus.png",
    "Suddenly_.png",
    "kick.png",
    "movement.png",
    "sports.png",
    "case_study_01.png",
    "flower_boy.png",
    "little_criminals.png",
    "stick_season.png",
    "pink_friday_2.png",
    "desolation_angels.png",
    "Making_Mirrors.png",
    "texas_hold_em.png",
    "Honky_Chateau.png",
    "cant_buy_a_thrill.png",
    "the_chronic.png"
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
