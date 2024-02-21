//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "never_enough.png",
    "once_bitten.png",
    "Monkey_Mania.png",
    "get_a_grip.png",
    "erratic_cinema.png",
    "aja.png",
    "pinkerton.png",
    "apolloxxI.png",
    "astro_lounge.png",
    "momints.png",
    "Late_Registration.png",
    "Demon_Days.png",
    "hysteria.png",
    "flirtin_with_disiaster.png",
    "they_might_be_giants.png",
    "Cool_Patrol.png",
    "Berhana.png",
    "The_Trinity.png",
    "Quaranta.png",
    "system_of_a_down.png",
    "Im_Just_Ken_.png",
    "3_feet_high.png",
    "Mandatory_Fun.png",
    "Funkentelechy_Vs._The_Placebo_Syndrome.png",
    "dr_feel_good.png",
    "case_study_01.png",
    "1988.png",
    "1989.png",
    "uh_huh.png",
    "blonde.png",
    "The_2nd_Law.png",
    "Blue_Moves.png",
    "Vaudeville_Villain.png",
    "SOUR.png",
    "Yours_Dreamily.png",
    "Suddenly_.png",
    "acid_rap.png",
    "MM...FOOD.png",
    "The_Life_Of_Pablo.png",
    "movement.png",
    "vampires_of_city.png",
    "MANIA.png",
    "ghosts.png",
    "Waiting_on_a_Song.png",
    "enema_of_the_state.png",
    "justice.png",
    "Rise_And_Fall_Rage_And_Grace.png",
    "Promise.png",
    "l-o-v-e.png",
    "cmon.png",
    "MONTERO.png",
    "sing_the_blues.png",
    "I_Never_Loved_a_Man_the_Way_I_Love_You.png",
    "testing.png",
    "lover.png",
    "The_Beginning.png",
    "thitvs.png",
    "recess.png",
    "pink_friday_2.png",
    "stick_season.png",
    "women_in_music_pt_III.png",
    "well_done.png",
    "slippery_when_wet.png",
    "innerspeaker.png",
    "little_criminals.png",
    "han.png",
    "an_evening_with_silk_sonic.png",
    "a_lot_about_livin.png",
    "streets_of_bolingbrook.png",
    "FALLING_OR_FLYING_.png",
    "very_special_christmas_2.png",
    "the_woman_in_me.png",
    "Madman_Across_The_Water.png",
    "cant_buy_a_thrill.png",
    "red_moon_in_venus.png",
    "pimp_a_butterfly.png",
    "human_after_all.png",
    "rocking_into_the_night.png",
    "The_Swing.png",
    "southern_nights.png",
    "minute_by_minute.png",
    "Egg_in_the_Backseat.png",
    "kick.png",
    "led_zeppelin_III.png",
    "mbdtf.png",
    "texas_hold_em.png",
    "the_score.png",
    "be_more.png",
    "Brothers.png",
    "traffic.png",
    "One_Wayne_G.png",
    "free_your_mind.png",
    "gunfighter_ballads.png",
    "new_eyes.png",
    "make_it_big.png",
    "The_Eminem_Show.png",
    "off_the_wall.png",
    "diver_down.png",
    "in_utero.png",
    "back_in_black.png",
    "The_College_Dropout.png",
    "desolation_angels.png",
    "best_of_sweet.png",
    "Time_Space.png",
    "her_love_still_haunts_me_like_a_ghost.png",
    "melophobia2.png",
    "Freudian.png",
    "WE_ARE_.png",
    "Lets_Rock.png",
    "cheryl.png",
    "speak_now.png",
    "Honky_Chateau.png",
    "GINGER.png",
    "Amen_.png",
    "monsters.png",
    "RENAISSANCE.png",
    "son_of_a_son_of_a_sailor.png",
    "Turn_Blue.png",
    "feels.png",
    "red.png",
    "KIDS_SEE_GHOSTS.png",
    "sports.png",
    "Man_On_The_Moon_II__The_Legend_Of_Mr._Rager.png",
    "flower_boy.png",
    "van_halen_II.png",
    "California_.png",
    "The_Carter_III.png",
    "Ugh_those_feels_again.png",
    "cage_the_elephant.png",
    "yeezus.png",
    "El_Camino.png",
    "top_gun.png",
    "american_teen.png",
    "private_space.png",
    "rubber_soul.png",
    "the_chronic.png",
    "Blood_Sugar_Sex_Magik_.png",
    "good_kid_maad_city.png",
    "channel_orange.png",
    "damn_the_torpedoes.png",
    "thee_sacred_souls.png",
    "questions.png",
    "oxnard.png",
    "starboy.png",
    "me.png",
    "Making_Mirrors.png"
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
