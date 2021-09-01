const urlParams = new URLSearchParams(location.search);
const questions = document.querySelectorAll(
  'div.question-content, div.answer'
);
let searchedPhrase;

for (const value of urlParams.values()) {
  searchedPhrase = value;
}

let regexPhrase = new RegExp(searchedPhrase, 'gi');

for (let i = 0; i < questions.length; i++) {
  let matchingElements = questions[i].innerText.match(regexPhrase);
  if (matchingElements) {
    let uniqueMatchingElements = matchingElements.filter(
      (value, index, self) => {
        return self.indexOf(value) === index;
      }
    );
    uniqueMatchingElements.forEach((element, index) => {
      let highlightedText =
        '<span class="phrase-colored">' + element + '</span>';
      questions[i].innerHTML = questions[i].innerHTML.replace(
        new RegExp(matchingElements[index], 'g'),
        highlightedText
      );
    });
  }
}
