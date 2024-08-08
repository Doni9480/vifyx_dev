function getCookie(name) {
    let cookieArr = document.cookie.split("; ");
    for(let i = 0; i < cookieArr.length; i++) {
        let cookiePair = cookieArr[i].split("=");
        if (name == cookiePair[0]) {
            return cookiePair[1];
        }
    }
    return null;
}

function check_referral_code(){
    // Получаем текущий URL
    let currentUrl = window.location.href;

    // Используем регулярное выражение для поиска параметра referral_code
    let referralCodeMatch = currentUrl.match(/\?(.*)/);

    let referralCode = null;

    if (referralCodeMatch) {
        referralCode = referralCodeMatch[1];
    }

    if (referralCode) {
        setTimeout(() => {
            document.querySelectorAll(".accordion-header")[1].click();
            console.log("clicking on header");
        }, 1000);
        return referralCode
    } else {
        return null;
    }
}
check_referral_code();
let form_login = document.querySelector('#login-form');
let form_register = document.querySelector('#register-form');

form_login.addEventListener('submit', login_send);
form_register.addEventListener('submit', register_send);

async function login_send(e) {
    e.preventDefault();

    let username = form_login.querySelector('input[name="username"]');
    let password = form_login.querySelector('input[name="password"]');
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');
    let csrftoken = form_login.querySelector('input[name="csrfmiddlewaretoken"').value;

    let obj = new Object();
    obj.username = username.value;
    obj.password = password.value;
    obj.g_recaptcha_response = g_recaptcha_response.value

    let form_data = JSON.stringify(obj);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/users/login/';

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    });

    get_g_token();


    if (response.ok) {
        let result = await response.json();

        form_errors = document.querySelectorAll('#form-error');

        for (const form_error of form_errors) {
            form_error.remove();
        }

        if (result.token) {
            document.cookie =`blog_access_token=${result.token};max-age=31536000;path=/`;

            var url = new URL(window.location.href);
            var next = url.searchParams.get("next");
            if (next) {
                window.location.replace(window.location.protocol + '//' + window.location.host + next);
            } else {
                window.location.replace(window.location.protocol + '//' + window.location.host + '/my/profile/');
            }

        } else {
            if (result.username) {
                username.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.username}</div>`);
            }

            if (result.password) {
                password.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.password}</div>`);
            }

            if (result.recaptcha) {
                form_login.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}

async function register_send(e) {
    e.preventDefault();

    let first_name = form_register.querySelector('input[name="first_name"]');
    let email = form_register.querySelector('input[name="email"]');
    let username = form_register.querySelector('input[name="username"]');
    let password = form_register.querySelector('input[name="password"]');
    let password2 = form_register.querySelector('input[name="password2"]');
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');
    let csrftoken = form_register.querySelector('input[name="csrfmiddlewaretoken"').value;

    let obj = new Object();
    obj.first_name = first_name.value;
    obj.email = email.value;
    obj.username = username.value;
    obj.password = password.value;
    obj.password2 = password2.value;
    obj.g_recaptcha_response = g_recaptcha_response.value;
    obj.language = navigator.language || navigator.userLanguage;

    let form_data = JSON.stringify(obj);

    referral = check_referral_code();
    if (referral === null) {
        url = window.location.protocol + '//' + window.location.host + '/api/v1/users/registration/';
    } else {
        url = window.location.protocol + '//' + window.location.host + '/api/v1/users/registration/?' + referral;
    }
    

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    });

    get_g_token();

    if (response.ok) {
        let result = await response.json();

        if (result.token) {
            document.cookie =`blog_access_token=${result.token};max-age=31536000;path=/`;

            var url = new URL(window.location.href);
            var next = url.searchParams.get("next");
            if (next) {
                window.location.replace(window.location.protocol + '//' + window.location.host + next);
            } else {
                window.location.replace(window.location.protocol + '//' + window.location.host + '/my/profile/');
            }
        } else {
            form_errors = document.querySelectorAll('#form-error');

            for (const form_error of form_errors) {
                form_error.remove();
            }

            if (result.first_name) {
                first_name.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.first_name}</div>`);
            }

            if (result.email) {
                email.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.email}</div>`);
            }

            if (result.username) {
                username.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.username}</div>`);
            }

            if (result.password) {
                password.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.password}</div>`);
            }

            if (result.password2) {
                password2.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.password2}</div>`);
            }

            if (result.recaptcha) {
                form_register.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}
