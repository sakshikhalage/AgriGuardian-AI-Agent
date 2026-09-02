const translations = {

    en: {
        title: "🌱 AgriGuardian AI Agent",
        subtitle: "Your Smart Farming Assistant",
        languageLabel: "Select Language:",
        placeholder: "Ask your farming question",
        askButton: "Ask AI"
    },

    hi: {
        title: "🌱 AgriGuardian AI एजेंट",
        subtitle: "आपका स्मार्ट कृषि सहायक",
        languageLabel: "भाषा चुनें:",
        placeholder: "अपना कृषि संबंधी प्रश्न पूछें",
        askButton: "AI से पूछें"
    },

    mr: {
        title: "🌱 AgriGuardian AI एजंट",
        subtitle: "तुमचा स्मार्ट शेती सहाय्यक",
        languageLabel: "भाषा निवडा:",
        placeholder: "तुमचा शेतीविषयक प्रश्न विचारा",
        askButton: "AI ला विचारा"
    }
};


function changeLanguage() {

    const language = document.getElementById("language").value;

    document.getElementById("title").innerText =
        translations[language].title;

    document.getElementById("subtitle").innerText =
        translations[language].subtitle;

    document.getElementById("languageLabel").innerText =
        translations[language].languageLabel;

    document.getElementById("question").placeholder =
        translations[language].placeholder;

    document.getElementById("askButton").innerText =
        translations[language].askButton;
}


async function askQuestion() {

    const question =
        document.getElementById("question").value;

    const answer =
        document.getElementById("answer");

    if (question === "") {
        answer.innerText = "Please enter a question.";
        return;
    }

    answer.innerText =
        "Connecting to AgriGuardian...";

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/ask",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                 question: question,
                 language: document.getElementById("language").value
               })            
           }
        );

        const data = await response.json();

        answer.innerText = data.answer;

    } catch (error) {

        answer.innerText =
            "Could not connect to AgriGuardian backend.";

    }
}