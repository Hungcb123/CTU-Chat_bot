const test = require('node:test');
const assert = require('node:assert/strict');

const {
    resizeUserInput,
    handleUserInputKeydown
} = require('../frontend/script.js');

test('chat input grows to its content and caps at six lines', () => {
    const shortInput = { scrollHeight: 72, style: {} };
    resizeUserInput(shortInput);
    assert.equal(shortInput.style.height, '72px');
    assert.equal(shortInput.style.overflowY, 'hidden');

    const longInput = { scrollHeight: 220, style: {} };
    resizeUserInput(longInput);
    assert.equal(longInput.style.height, '144px');
    assert.equal(longInput.style.overflowY, 'auto');
});

test('Enter submits while Shift+Enter and IME composition keep editing', () => {
    let submissions = 0;
    const form = { requestSubmit: () => submissions++ };
    const enter = {
        key: 'Enter', shiftKey: false, isComposing: false,
        preventDefault() { this.prevented = true; }
    };

    handleUserInputKeydown(enter, form);
    assert.equal(enter.prevented, true);
    assert.equal(submissions, 1);

    handleUserInputKeydown({ key: 'Enter', shiftKey: true }, form);
    handleUserInputKeydown({ key: 'Enter', shiftKey: false, isComposing: true }, form);
    assert.equal(submissions, 1);
});
