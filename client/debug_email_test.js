// Debug email validation
const email = 'invalid-email';
console.log('Email:', email);
console.log('email.trim():', email.trim());
console.log('!email.trim():', !email.trim());
console.log('Regex test:', /\S+@\S+\.\S+/.test(email));
console.log('Should show invalid email error:', email.trim() && !/\S+@\S+\.\S+/.test(email));

// Test the validation logic flow
const validateEmail = (email) => {
  if (!email.trim()) {
    return "email is required";
  } else if (!/\S+@\S+\.\S+/.test(email)) {
    return "please enter a valid email";
  }
  return null;
};

console.log('Validation result for "invalid-email":', validateEmail('invalid-email'));
console.log('Validation result for "":', validateEmail(''));
console.log('Validation result for "test@example.com":', validateEmail('test@example.com'));
