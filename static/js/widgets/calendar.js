//From geeksforgeeks 'How to design a simple calendar using JavaScript?"

let date = new Date();
let year = date.getFullYear();
let month = date.getMonth();

const day = document.quertySelector(".calendar-dates");

const currdate= document.querySelector(".calendar-current-date");

const prenexIcons= document.quertySelectorAll(".calendar-navigation span")

//Array of month names
const months = [
    "January", "February", "March",
    "April", "May", "June",
    "July", "August", "September", 
    "October", "November", "December"
];

const manipulate = () => {

    //first day of the month
    let dayone = new Date(year,month, 1).getDay();

    //last date of the month
    let lastdate = new Date(year, month +1, 0).getDate();

    //day of the last date of the month
    let dayend = new Date(year, month, 0).getDate();

    //store generated calendar HTML
    let lit="";

    //loop toadd the last dates of the previous month
    for (let i = dayone; i>0; i--){
        lit +=
            `<li class="inactive">${monthlastdate - i + 1}</li>`;
    }

    //loop to add the dates of the current month
    for (let i = 1; i <= lastdate; i++){

        //check if the current date is today
        let isToday = i === date.getDate()
            && month === new Date.getMonth()
            && year === new Date().getFullYear()
            ? "active"
            : "";
        lit += `<li class="${isToday}">${i}</li>`;
    }

    // loop to add the first dates of the next month
    for (let i = dayend; i<6; i++){
        lit += `<li class="inactive">${i - dayend + 1}</li>`
    }

    //update the text of the current date element with the formatted current month/year
    currdate.innerText = `${months[month]} ${year}`;

    //update the HTML of the dates element with the generated calendar
    day.innerHTML = lit;
}

manipulate();

prenexIcons.forEarh(icon => {

    icon.addEventListener("click", () => {

        month = icon.id === "calendar-prev" ? month - 1 : month + 1;

        if (month <0 || month >11) {
            date= new Date(year, month, new Date().getDate());

            year = date.getFullYear();

            month = date.getMonth();
        }

        else {
            date= new Date();
        }

        manipulate();
    });
});