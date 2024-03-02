//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "Quaranta.png",
    "texas_hold_em.png",
    "Brothers.png",
    "California_.png",
    "human_after_all.png",
    "Cooleyhighharmony_Bonus_Tracks_Version.png",
    "damn_the_torpedoes.png",
    "be_more.png",
    "Baduizm.png",
    "momints.png",
    "Lets_Rock.png",
    "movement.png",
    "Blue_Moves.png",
    "FALLING_OR_FLYING_.png",
    "Waiting_on_a_Song.png",
    "The_Beginning.png",
    "american_teen.png",
    "back_in_black.png",
    "1989.png",
    "3_feet_high.png",
    "Freudian.png",
    "Berhana.png",
    "top_gun.png",
    "oxnard.png",
    "make_it_big.png",
    "the_chronic.png",
    "Vaudeville_Villain.png",
    "MANIA.png",
    "ghosts.png",
    "off_the_wall.png",
    "private_space.png",
    "Suddenly_.png",
    "free_your_mind.png",
    "Madman_Across_The_Water.png",
    "The_Life_Of_Pablo.png",
    "lover.png",
    "Macadelic.png",
    "melophobia2.png",
    "me.png",
    "in_utero.png",
    "One_Wayne_G.png",
    "case_study_01.png",
    "flower_boy.png",
    "slippery_when_wet.png",
    "astro_lounge.png",
    "get_a_grip.png",
    "yeezus.png",
    "mbdtf.png",
    "cage_the_elephant.png",
    "The_Message.png",
    "apolloxxI.png",
    "the_score.png",
    "system_of_a_down.png",
    "gaucho.png",
    "innerspeaker.png",
    "a_lot_about_livin.png",
    "monsters.png",
    "Return_of_the_Mack.png",
    "The_Trinity.png",
    "dr_feel_good.png",
    "rubber_soul.png",
    "GINGER.png",
    "blonde.png",
    "best_of_sweet.png",
    "thee_sacred_souls.png",
    "cant_buy_a_thrill.png",
    "son_of_a_son_of_a_sailor.png",
    "illinois_poster.png",
    "Funkentelechy_Vs._The_Placebo_Syndrome.png",
    "KIDS_SEE_GHOSTS.png",
    "tracychapman_poster.png",
    "1988.png",
    "The_Eminem_Show.png",
    "never_enough.png",
    "MM...FOOD.png",
    "good_kid_maad_city.png",
    "MONTERO.png",
    "gunfighter_ballads.png",
    "Late_Registration.png",
    "vampires_of_city.png",
    "an_evening_with_silk_sonic.png",
    "Mandatory_Fun.png",
    "Cool_Patrol.png",
    "diver_down.png",
    "The_Swing.png",
    "Gemini_Rights.png",
    "red.png",
    "uh_huh.png",
    "Amen_.png",
    "han.png",
    "speak_now.png",
    "The_Carter_III.png",
    "recess.png",
    "channel_orange.png",
    "erratic_cinema.png",
    "questions.png",
    "cmon.png",
    "her_love_still_haunts_me_like_a_ghost.png",
    "Rise_And_Fall_Rage_And_Grace.png",
    "red_moon_in_venus.png",
    "aja.png",
    "Ugh_those_feels_again.png",
    "women_in_music_pt_III.png",
    "pimp_a_butterfly.png",
    "Monkey_Mania.png",
    "once_bitten.png",
    "Blood_Sugar_Sex_Magik_.png",
    "van_halen_II.png",
    "thitvs.png",
    "new_eyes.png",
    "Man_On_The_Moon_II__The_Legend_Of_Mr._Rager.png",
    "Honky_Chateau.png",
    "little_criminals.png",
    "enema_of_the_state.png",
    "stick_season.png",
    "pink_friday_2.png",
    "streets_of_bolingbrook.png",
    "WE_ARE_.png",
    "Im_Just_Ken_.png",
    "testing.png",
    "very_special_christmas_2.png",
    "the_woman_in_me.png",
    "The_2nd_Law.png",
    "sing_the_blues.png",
    "Yours_Dreamily.png",
    "justice.png",
    "led_zeppelin_III.png",
    "Egg_in_the_Backseat.png",
    "cheryl.png",
    "I_Never_Loved_a_Man_the_Way_I_Love_You.png",
    "rocking_into_the_night.png",
    "starboy.png",
    "The_College_Dropout.png",
    "Eternal_Atake.png",
    "they_might_be_giants.png",
    "pinkerton.png",
    "Promise.png",
    "Turn_Blue.png",
    "Time_Space.png",
    "A_Seat_at_the_Table.png",
    "hysteria.png",
    "well_done.png",
    "traffic.png",
    "SOUR.png",
    "El_Camino.png",
    "sports.png",
    "acid_rap.png",
    "RENAISSANCE.png",
    "SOS.png",
    "l-o-v-e.png",
    "feels.png",
    "ChappellRoan_poster.png",
    "Making_Mirrors.png",
    "Demon_Days.png",
    "kick.png",
    "southern_nights.png",
    "desolation_angels.png",
    "minute_by_minute.png",
    "flirtin_with_disiaster.png"
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
