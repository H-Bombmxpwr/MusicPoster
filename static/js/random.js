//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "new_eyes.png",
    "back_in_black.png",
    "private_space.png",
    "Im_Just_Ken_.png",
    "starboy.png",
    "once_bitten.png",
    "1988.png",
    "3_feet_high.png",
    "Lets_Rock.png",
    "The_Eminem_Show.png",
    "they_might_be_giants.png",
    "Turn_Blue.png",
    "One_Wayne_G.png",
    "Ugh_those_feels_again.png",
    "The_Swing.png",
    "feels.png",
    "KIDS_SEE_GHOSTS.png",
    "little_criminals.png",
    "The_2nd_Law.png",
    "justice.png",
    "get_a_grip.png",
    "sing_the_blues.png",
    "system_of_a_down.png",
    "questions.png",
    "RENAISSANCE.png",
    "be_more.png",
    "gunfighter_ballads.png",
    "A_Seat_at_the_Table.png",
    "cheryl.png",
    "slippery_when_wet.png",
    "son_of_a_son_of_a_sailor.png",
    "Gemini_Rights.png",
    "the_chronic.png",
    "red.png",
    "California_.png",
    "apolloxxI.png",
    "The_Trinity.png",
    "Eternal_Atake.png",
    "Demon_Days.png",
    "red_moon_in_venus.png",
    "Quaranta.png",
    "pimp_a_butterfly.png",
    "Making_Mirrors.png",
    "pinkerton.png",
    "damn_the_torpedoes.png",
    "innerspeaker.png",
    "make_it_big.png",
    "dr_feel_good.png",
    "her_love_still_haunts_me_like_a_ghost.png",
    "Monkey_Mania.png",
    "minute_by_minute.png",
    "ghosts.png",
    "testing.png",
    "vampires_of_city.png",
    "traffic.png",
    "Blue_Moves.png",
    "free_your_mind.png",
    "uh_huh.png",
    "Vaudeville_Villain.png",
    "Baduizm.png",
    "cant_buy_a_thrill.png",
    "sports.png",
    "recess.png",
    "well_done.png",
    "never_enough.png",
    "best_of_sweet.png",
    "diver_down.png",
    "the_woman_in_me.png",
    "Berhana.png",
    "The_Life_Of_Pablo.png",
    "an_evening_with_silk_sonic.png",
    "illinois_poster.png",
    "stick_season.png",
    "Egg_in_the_Backseat.png",
    "off_the_wall.png",
    "cage_the_elephant.png",
    "El_Camino.png",
    "Suddenly_.png",
    "MONTERO.png",
    "Indigo_Jack__The_New_World_Border.png",
    "Cool_Kids_(Sped_Up).png",
    "southern_nights.png",
    "a_lot_about_livin.png",
    "very_special_christmas_2.png",
    "aja.png",
    "The_College_Dropout.png",
    "SOS.png",
    "case_study_01.png",
    "Time_Space.png",
    "Waiting_on_a_Song.png",
    "blonde.png",
    "me.png",
    "Freudian.png",
    "enema_of_the_state.png",
    "1989.png",
    "yeezus.png",
    "good_kid_maad_city.png",
    "streets_of_bolingbrook.png",
    "Rise_And_Fall_Rage_And_Grace.png",
    "the_score.png",
    "ChappellRoan_poster.png",
    "The_Message.png",
    "flirtin_with_disiaster.png",
    "lover.png",
    "rocking_into_the_night.png",
    "MM...FOOD.png",
    "gaucho.png",
    "Honky_Chateau.png",
    "WE_ARE_.png",
    "The_Carter_III.png",
    "Brothers.png",
    "kick.png",
    "human_after_all.png",
    "astro_lounge.png",
    "Return_of_the_Mack.png",
    "GINGER.png",
    "tracychapman_poster.png",
    "van_halen_II.png",
    "Cooleyhighharmony_Bonus_Tracks_Version.png",
    "Blood_Sugar_Sex_Magik_.png",
    "rubber_soul.png",
    "speak_now.png",
    "Funkentelechy_Vs._The_Placebo_Syndrome.png",
    "thitvs.png",
    "desolation_angels.png",
    "FALLING_OR_FLYING_.png",
    "thee_sacred_souls.png",
    "oxnard.png",
    "movement.png",
    "Madman_Across_The_Water.png",
    "melophobia2.png",
    "flower_boy.png",
    "channel_orange.png",
    "women_in_music_pt_III.png",
    "Mandatory_Fun.png",
    "SOUR.png",
    "Macadelic.png",
    "monsters.png",
    "led_zeppelin_III.png",
    "Amen_.png",
    "Man_On_The_Moon_II__The_Legend_Of_Mr._Rager.png",
    "in_utero.png",
    "The_Beginning.png",
    "Late_Registration.png",
    "l-o-v-e.png",
    "american_teen.png",
    "Yours_Dreamily.png",
    "mbdtf.png",
    "I_Never_Loved_a_Man_the_Way_I_Love_You.png",
    "hysteria.png",
    "erratic_cinema.png",
    "Cool_Patrol.png",
    "Promise.png",
    "MANIA.png",
    "pink_friday_2.png",
    "acid_rap.png",
    "han.png",
    "cmon.png",
    "texas_hold_em.png",
    "momints.png",
    "top_gun.png"
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
