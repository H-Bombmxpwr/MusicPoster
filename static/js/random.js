//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "pinkerton.png",
    "van_halen_II.png",
    "Blood_Sugar_Sex_Magik_.png",
    "cmon.png",
    "Amen_.png",
    "MANIA.png",
    "cage_the_elephant.png",
    "innerspeaker.png",
    "Promise.png",
    "women_in_music_pt_III.png",
    "KIDS_SEE_GHOSTS.png",
    "channel_orange.png",
    "acid_rap.png",
    "traffic.png",
    "good_kid_maad_city.png",
    "Monkey_Mania.png",
    "thitvs.png",
    "minute_by_minute.png",
    "me.png",
    "little_criminals.png",
    "California_.png",
    "Funkentelechy_Vs._The_Placebo_Syndrome.png",
    "be_more.png",
    "Ugh_those_feels_again.png",
    "han.png",
    "desolation_angels.png",
    "Waiting_on_a_Song.png",
    "aja.png",
    "in_utero.png",
    "cant_buy_a_thrill.png",
    "yeezus.png",
    "rubber_soul.png",
    "very_special_christmas_2.png",
    "diver_down.png",
    "starboy.png",
    "mbdtf.png",
    "momints.png",
    "Vaudeville_Villain.png",
    "texas_hold_em.png",
    "feels.png",
    "the_chronic.png",
    "lover.png",
    "recess.png",
    "new_eyes.png",
    "Berhana.png",
    "Freudian.png",
    "get_a_grip.png",
    "Time_Space.png",
    "movement.png",
    "flower_boy.png",
    "son_of_a_son_of_a_sailor.png",
    "cheryl.png",
    "sing_the_blues.png",
    "l-o-v-e.png",
    "human_after_all.png",
    "speak_now.png",
    "1989.png",
    "dr_feel_good.png",
    "red.png",
    "top_gun.png",
    "Yours_Dreamily.png",
    "El_Camino.png",
    "monsters.png",
    "southern_nights.png",
    "well_done.png",
    "an_evening_with_silk_sonic.png",
    "system_of_a_down.png",
    "The_Beginning.png",
    "Im_Just_Ken_.png",
    "The_Life_Of_Pablo.png",
    "Honky_Chateau.png",
    "thee_sacred_souls.png",
    "ghosts.png",
    "the_woman_in_me.png",
    "Man_On_The_Moon_II__The_Legend_Of_Mr._Rager.png",
    "case_study_01.png",
    "blonde.png",
    "damn_the_torpedoes.png",
    "The_Trinity.png",
    "rocking_into_the_night.png",
    "red_moon_in_venus.png",
    "Brothers.png",
    "SOUR.png",
    "hysteria.png",
    "uh_huh.png",
    "once_bitten.png",
    "apolloxxI.png",
    "Lets_Rock.png",
    "The_2nd_Law.png",
    "RENAISSANCE.png",
    "GINGER.png",
    "slippery_when_wet.png",
    "her_love_still_haunts_me_like_a_ghost.png",
    "best_of_sweet.png",
    "gunfighter_ballads.png",
    "pimp_a_butterfly.png",
    "vampires_of_city.png",
    "3_feet_high.png",
    "Cool_Patrol.png",
    "1988.png",
    "led_zeppelin_III.png",
    "they_might_be_giants.png",
    "Egg_in_the_Backseat.png",
    "oxnard.png",
    "WE_ARE_.png",
    "One_Wayne_G.png",
    "testing.png",
    "Late_Registration.png",
    "Macadelic.png",
    "enema_of_the_state.png",
    "astro_lounge.png",
    "The_Eminem_Show.png",
    "Turn_Blue.png",
    "Gemini_Rights.png",
    "off_the_wall.png",
    "Madman_Across_The_Water.png",
    "ChappellRoan_poster.png",
    "free_your_mind.png",
    "the_score.png",
    "MM...FOOD.png",
    "stick_season.png",
    "Quaranta.png",
    "Rise_And_Fall_Rage_And_Grace.png",
    "Demon_Days.png",
    "melophobia2.png",
    "sports.png",
    "flirtin_with_disiaster.png",
    "Suddenly_.png",
    "streets_of_bolingbrook.png",
    "make_it_big.png",
    "Return_of_the_Mack.png",
    "tracychapman_poster.png",
    "pink_friday_2.png",
    "MONTERO.png",
    "kick.png",
    "private_space.png",
    "questions.png",
    "illinois_poster.png",
    "justice.png",
    "a_lot_about_livin.png",
    "Blue_Moves.png",
    "Eternal_Atake.png",
    "never_enough.png",
    "The_Swing.png",
    "american_teen.png",
    "FALLING_OR_FLYING_.png",
    "Making_Mirrors.png",
    "I_Never_Loved_a_Man_the_Way_I_Love_You.png",
    "The_Carter_III.png",
    "Mandatory_Fun.png",
    "The_Message.png",
    "The_College_Dropout.png",
    "erratic_cinema.png",
    "back_in_black.png"
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
