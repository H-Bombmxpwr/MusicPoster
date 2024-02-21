//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "cage_the_elephant.png",
    "texas_hold_em.png",
    "the_score.png",
    "human_after_all.png",
    "hysteria.png",
    "off_the_wall.png",
    "The_Carter_III.png",
    "van_halen_II.png",
    "women_in_music_pt_III.png",
    "MM...FOOD.png",
    "her_love_still_haunts_me_like_a_ghost.png",
    "red_moon_in_venus.png",
    "aja.png",
    "KIDS_SEE_GHOSTS.png",
    "Making_Mirrors.png",
    "vampires_of_city.png",
    "feels.png",
    "GINGER.png",
    "southern_nights.png",
    "RENAISSANCE.png",
    "ghosts.png",
    "speak_now.png",
    "streets_of_bolingbrook.png",
    "Blood_Sugar_Sex_Magik_.png",
    "The_2nd_Law.png",
    "The_Trinity.png",
    "Blue_Moves.png",
    "I_Never_Loved_a_Man_the_Way_I_Love_You.png",
    "1989.png",
    "stick_season.png",
    "FALLING_OR_FLYING_.png",
    "Mandatory_Fun.png",
    "The_Eminem_Show.png",
    "pinkerton.png",
    "get_a_grip.png",
    "flirtin_with_disiaster.png",
    "Turn_Blue.png",
    "Amen_.png",
    "free_your_mind.png",
    "channel_orange.png",
    "Ugh_those_feels_again.png",
    "they_might_be_giants.png",
    "pink_friday_2.png",
    "Waiting_on_a_Song.png",
    "Freudian.png",
    "diver_down.png",
    "case_study_01.png",
    "desolation_angels.png",
    "MONTERO.png",
    "Yours_Dreamily.png",
    "thitvs.png",
    "slippery_when_wet.png",
    "in_utero.png",
    "starboy.png",
    "an_evening_with_silk_sonic.png",
    "Funkentelechy_Vs._The_Placebo_Syndrome.png",
    "a_lot_about_livin.png",
    "pimp_a_butterfly.png",
    "the_chronic.png",
    "The_Beginning.png",
    "Demon_Days.png",
    "astro_lounge.png",
    "private_space.png",
    "kick.png",
    "mbdtf.png",
    "Honky_Chateau.png",
    "The_Life_Of_Pablo.png",
    "recess.png",
    "best_of_sweet.png",
    "El_Camino.png",
    "american_teen.png",
    "rubber_soul.png",
    "top_gun.png",
    "cant_buy_a_thrill.png",
    "ChappellRoan_poster.png",
    "Rise_And_Fall_Rage_And_Grace.png",
    "han.png",
    "Egg_in_the_Backseat.png",
    "melophobia2.png",
    "cmon.png",
    "damn_the_torpedoes.png",
    "little_criminals.png",
    "acid_rap.png",
    "Time_Space.png",
    "SOUR.png",
    "led_zeppelin_III.png",
    "blonde.png",
    "very_special_christmas_2.png",
    "Late_Registration.png",
    "California_.png",
    "Cool_Patrol.png",
    "lover.png",
    "good_kid_maad_city.png",
    "Suddenly_.png",
    "thee_sacred_souls.png",
    "justice.png",
    "Vaudeville_Villain.png",
    "monsters.png",
    "yeezus.png",
    "well_done.png",
    "apolloxxI.png",
    "WE_ARE_.png",
    "MANIA.png",
    "red.png",
    "Im_Just_Ken_.png",
    "movement.png",
    "The_College_Dropout.png",
    "sports.png",
    "erratic_cinema.png",
    "minute_by_minute.png",
    "Lets_Rock.png",
    "me.png",
    "innerspeaker.png",
    "Berhana.png",
    "the_woman_in_me.png",
    "gunfighter_ballads.png",
    "be_more.png",
    "questions.png",
    "back_in_black.png",
    "One_Wayne_G.png",
    "dr_feel_good.png",
    "system_of_a_down.png",
    "uh_huh.png",
    "son_of_a_son_of_a_sailor.png",
    "Monkey_Mania.png",
    "momints.png",
    "oxnard.png",
    "l-o-v-e.png",
    "traffic.png",
    "Promise.png",
    "tracychapman_poster.png",
    "flower_boy.png",
    "3_feet_high.png",
    "Man_On_The_Moon_II__The_Legend_Of_Mr._Rager.png",
    "illinois_poster.png",
    "enema_of_the_state.png",
    "rocking_into_the_night.png",
    "Quaranta.png",
    "once_bitten.png",
    "never_enough.png",
    "The_Swing.png",
    "testing.png",
    "cheryl.png",
    "1988.png",
    "Madman_Across_The_Water.png",
    "sing_the_blues.png",
    "Brothers.png",
    "new_eyes.png",
    "make_it_big.png"
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
