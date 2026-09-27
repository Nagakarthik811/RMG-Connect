// Display the sample employee identifiers without exposing the source-company prefix.
export function displayEmployeeId(value = '') {
  return String(value).replace(/^TCS(?=\d)/i, 'ABC');
}

export function displayEmail(value = '') {
  return String(value).replace(/@tcs\.com$/i, '@abc.com');
}

export function displayFormValue(key, value = '') {
  if (key === 'employee_id') return displayEmployeeId(value);
  if (key === 'email') return displayEmail(value);
  return value;
}
