//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "Demon_Days.png",
    "Making_Mirrors.png",
    "gunfighter_ballads.png",
    "Vaudeville_Villain.png",
    "off_the_wall.png",
    "The_Trinity.png",
    "yeezus.png",
    "top_gun.png",
    "SOS.png",
    "flirtin_with_disiaster.png",
    "her_love_still_haunts_me_like_a_ghost.png",
    "well_done.png",
    "starboy.png",
    "han.png",
    "Gemini_Rights.png",
    "Quaranta.png",
    "El_Camino.png",
    "good_kid_maad_city.png",
    "uh_huh.png",
    "Blood_Sugar_Sex_Magik_.png",
    "The_2nd_Law.png",
    "dr_feel_good.png",
    "in_utero.png",
    "Short_n_Sweet.png",
    "questions.png",
    "feels.png",
    "Cool_Kids_(Sped_Up).png",
    "Im_Just_Ken_.png",
    "1989.png",
    "illinois_poster.png",
    "GINGER.png",
    "Mandatory_Fun.png",
    "a_lot_about_livin.png",
    "once_bitten.png",
    "american_teen.png",
    "Cooleyhighharmony_Bonus_Tracks_Version.png",
    "Ugh_those_feels_again.png",
    "an_evening_with_silk_sonic.png",
    "The_Swing.png",
    "One_Wayne_G.png",
    "pink_friday_2.png",
    "innerspeaker.png",
    "acid_rap.png",
    "get_a_grip.png",
    "RENAISSANCE.png",
    "women_in_music_pt_III.png",
    "stick_season.png",
    "Eternal_Atake.png",
    "little_criminals.png",
    "case_study_01.png",
    "Egg_in_the_Backseat.png",
    "the_score.png",
    "Suddenly_.png",
    "Funkentelechy_Vs._The_Placebo_Syndrome.png",
    "Madman_Across_The_Water.png",
    "enema_of_the_state.png",
    "thee_sacred_souls.png",
    "streets_of_bolingbrook.png",
    "gaucho.png",
    "kick.png",
    "make_it_big.png",
    "oxnard.png",
    "The_Carter_III.png",
    "ghosts.png",
    "Macadelic.png",
    "Yours_Dreamily.png",
    "momints.png",
    "Big_Ideas.png",
    "1988.png",
    "ChappellRoan_poster.png",
    "the_chronic.png",
    "sing_the_blues.png",
    "Berhana.png",
    "Scarlet.png",
    "cheryl.png",
    "Wasteland,_Baby!.png",
    "Blue_Moves.png",
    "MANIA.png",
    "cant_buy_a_thrill.png",
    "mbdtf.png",
    "the_woman_in_me.png",
    "cmon.png",
    "WE_ARE_.png",
    "slippery_when_wet.png",
    "flower_boy.png",
    "thitvs.png",
    "red.png",
    "Man_On_The_Moon_II__The_Legend_Of_Mr._Rager.png",
    "testing.png",
    "FALLING_OR_FLYING_.png",
    "movement.png",
    "SOUR.png",
    "son_of_a_son_of_a_sailor.png",
    "Waiting_on_a_Song.png",
    "led_zeppelin_III.png",
    "I_Never_Loved_a_Man_the_Way_I_Love_You.png",
    "California_.png",
    "Promise.png",
    "rubber_soul.png",
    "never_enough.png",
    "pinkerton.png",
    "Brothers.png",
    "texas_hold_em.png",
    "new_eyes.png",
    "Freudian.png",
    "aja.png",
    "hysteria.png",
    "tracychapman_poster.png",
    "best_of_sweet.png",
    "Monkey_Mania.png",
    "me.png",
    "Time_Space.png",
    "channel_orange.png",
    "The_Eminem_Show.png",
    "traffic.png",
    "The_College_Dropout.png",
    "Turn_Blue.png",
    "back_in_black.png",
    "speak_now.png",
    "minute_by_minute.png",
    "system_of_a_down.png",
    "A_Seat_at_the_Table.png",
    "l-o-v-e.png",
    "3_feet_high.png",
    "MM...FOOD.png",
    "sports.png",
    "rocking_into_the_night.png",
    "private_space.png",
    "justice.png",
    "damn_the_torpedoes.png",
    "blonde.png",
    "erratic_cinema.png",
    "very_special_christmas_2.png",
    "cage_the_elephant.png",
    "Late_Registration.png",
    "pimp_a_butterfly.png",
    "The_Message.png",
    "recess.png",
    "Return_of_the_Mack.png",
    "The_Beginning.png",
    "Cool_Patrol.png",
    "they_might_be_giants.png",
    "desolation_angels.png",
    "van_halen_II.png",
    "Indigo_Jack__The_New_World_Border.png",
    "apolloxxI.png",
    "human_after_all.png",
    "vampires_of_city.png",
    "KIDS_SEE_GHOSTS.png",
    "MONTERO.png",
    "astro_lounge.png",
    "monsters.png",
    "Lets_Rock.png",
    "diver_down.png",
    "red_moon_in_venus.png",
    "melophobia2.png",
    "The_Life_Of_Pablo.png",
    "Rise_And_Fall_Rage_And_Grace.png",
    "Amen_.png",
    "Honky_Chateau.png",
    "free_your_mind.png",
    "southern_nights.png",
    "Baduizm.png",
    "be_more.png",
    "lover.png"
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
