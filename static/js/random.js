//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "Mandatory_Fun.png",
    "texas_hold_em.png",
    "The_Life_Of_Pablo.png",
    "SOS.png",
    "WE_ARE_.png",
    "Eternal_Atake.png",
    "the_chronic.png",
    "ChappellRoan_poster.png",
    "a_lot_about_livin.png",
    "Turn_Blue.png",
    "off_the_wall.png",
    "get_a_grip.png",
    "innerspeaker.png",
    "Monkey_Mania.png",
    "gunfighter_ballads.png",
    "the_woman_in_me.png",
    "speak_now.png",
    "very_special_christmas_2.png",
    "Im_Just_Ken_.png",
    "little_criminals.png",
    "thee_sacred_souls.png",
    "recess.png",
    "Cool_Patrol.png",
    "they_might_be_giants.png",
    "monsters.png",
    "The_Carter_III.png",
    "sports.png",
    "MANIA.png",
    "cage_the_elephant.png",
    "channel_orange.png",
    "illinois_poster.png",
    "GINGER.png",
    "Lets_Rock.png",
    "pinkerton.png",
    "Freudian.png",
    "erratic_cinema.png",
    "melophobia2.png",
    "questions.png",
    "hysteria.png",
    "1989.png",
    "well_done.png",
    "once_bitten.png",
    "feels.png",
    "cant_buy_a_thrill.png",
    "Quaranta.png",
    "Madman_Across_The_Water.png",
    "rocking_into_the_night.png",
    "her_love_still_haunts_me_like_a_ghost.png",
    "The_2nd_Law.png",
    "MM...FOOD.png",
    "me.png",
    "led_zeppelin_III.png",
    "traffic.png",
    "desolation_angels.png",
    "stick_season.png",
    "The_Beginning.png",
    "pink_friday_2.png",
    "astro_lounge.png",
    "The_College_Dropout.png",
    "movement.png",
    "be_more.png",
    "apolloxxI.png",
    "an_evening_with_silk_sonic.png",
    "1988.png",
    "l-o-v-e.png",
    "never_enough.png",
    "ghosts.png",
    "diver_down.png",
    "van_halen_II.png",
    "Gemini_Rights.png",
    "red_moon_in_venus.png",
    "rubber_soul.png",
    "The_Message.png",
    "Man_On_The_Moon_II__The_Legend_Of_Mr._Rager.png",
    "starboy.png",
    "red.png",
    "top_gun.png",
    "son_of_a_son_of_a_sailor.png",
    "damn_the_torpedoes.png",
    "Baduizm.png",
    "yeezus.png",
    "3_feet_high.png",
    "Blood_Sugar_Sex_Magik_.png",
    "flirtin_with_disiaster.png",
    "Cooleyhighharmony_Bonus_Tracks_Version.png",
    "thitvs.png",
    "Funkentelechy_Vs._The_Placebo_Syndrome.png",
    "Making_Mirrors.png",
    "RENAISSANCE.png",
    "american_teen.png",
    "women_in_music_pt_III.png",
    "sing_the_blues.png",
    "Promise.png",
    "Amen_.png",
    "Vaudeville_Villain.png",
    "blonde.png",
    "in_utero.png",
    "streets_of_bolingbrook.png",
    "new_eyes.png",
    "vampires_of_city.png",
    "Blue_Moves.png",
    "uh_huh.png",
    "kick.png",
    "SOUR.png",
    "KIDS_SEE_GHOSTS.png",
    "flower_boy.png",
    "California_.png",
    "The_Eminem_Show.png",
    "Ugh_those_feels_again.png",
    "momints.png",
    "MONTERO.png",
    "testing.png",
    "private_space.png",
    "El_Camino.png",
    "Brothers.png",
    "back_in_black.png",
    "the_score.png",
    "minute_by_minute.png",
    "oxnard.png",
    "Time_Space.png",
    "A_Seat_at_the_Table.png",
    "cheryl.png",
    "good_kid_maad_city.png",
    "Suddenly_.png",
    "pimp_a_butterfly.png",
    "mbdtf.png",
    "system_of_a_down.png",
    "The_Swing.png",
    "Berhana.png",
    "dr_feel_good.png",
    "FALLING_OR_FLYING_.png",
    "lover.png",
    "enema_of_the_state.png",
    "free_your_mind.png",
    "I_Never_Loved_a_Man_the_Way_I_Love_You.png",
    "acid_rap.png",
    "aja.png",
    "Return_of_the_Mack.png",
    "make_it_big.png",
    "southern_nights.png",
    "Yours_Dreamily.png",
    "One_Wayne_G.png",
    "Late_Registration.png",
    "human_after_all.png",
    "slippery_when_wet.png",
    "justice.png",
    "cmon.png",
    "Waiting_on_a_Song.png",
    "Macadelic.png",
    "tracychapman_poster.png",
    "Honky_Chateau.png",
    "Egg_in_the_Backseat.png",
    "case_study_01.png",
    "Rise_And_Fall_Rage_And_Grace.png",
    "The_Trinity.png",
    "han.png",
    "Demon_Days.png",
    "best_of_sweet.png"
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
