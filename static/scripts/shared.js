const addUserModal = document.getElementById('add-modal');
const backdrop = document.getElementById('backdrop');
const startAddUserButton = document.querySelector('header a#sign-up');
const cancelAddUserButton = addUserModal.querySelector('.btn--passive');
const confirmAddUserButton = cancelAddUserButton.nextElementSibling;
const userInputs = addUserModal.querySelectorAll('input');
const backdropRegister = document.getElementById('backdrop-register');
const removeRegisterModal = document.querySelector('.modal-success');


const toggleBackdrop = () => {
  backdrop.classList.toggle('visible');
};

const toggleBackdropRegister = () => {
  backdropRegister.classList.toggle('visible');
};

const closeUserModal = () => {
  addUserModal.classList.remove('visible');
};

const closeRegisterModal = () => {
  removeRegisterModal.classList.remove('visible');
};

const showUserModal = () => {
  addUserModal.classList.toggle('visible');
  toggleBackdrop();
};

const clearUserInput = () => {
  for (const input of userInputs) {
    input.value = '';
  }
};

const backdropClickHandler = () => {
  clearUserInput();
  toggleBackdrop();
  closeUserModal();
};

const cancelAddUserHandler = () => {
  closeUserModal();
  toggleBackdrop();
  clearUserInput();
};

const changeButtonType = () => {
  confirmAddUserButton.setAttribute('type', 'submit')
}

const addUserHandler = () => {
  const emailValue = userInputs[0].value;
  const passwordValue = userInputs[1].value;
  if (
    emailValue.trim() === '' || !emailValue.includes('@') ||
    passwordValue.trim() === '') {
    alert('Please enter valid values!');
    return;
  }

  closeUserModal();
  toggleBackdrop();
  changeButtonType();
};

const backdropRegisterClickHandler = () => {
  closeRegisterModal();
  toggleBackdropRegister();
};

startAddUserButton.addEventListener('click', showUserModal);
backdrop.addEventListener('click', backdropClickHandler);
cancelAddUserButton.addEventListener('click', cancelAddUserHandler);
confirmAddUserButton.addEventListener('click', addUserHandler);
backdropRegister.addEventListener('click', backdropRegisterClickHandler);