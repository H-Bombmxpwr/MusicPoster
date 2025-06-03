

const buttonSection = document.querySelector('.buttons');


class spinner {
    cosntructor(name){
        this.name = name;
        this.element = null;
    }
}

const template = document.querySelector('#spinner-template');
const clone = template.content.cloneNode(true);
spinner.element = clone.querySelector('#loader-div');

const button2 = document.querySelector('.search');

button2.addEventListener('click', replaceButtons);

function replaceButtons() {

    //buttonSection.replaceWith(spinner.element);   
    
}


   
