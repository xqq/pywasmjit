(function () {
	var PLAY_SAMPLES = [
		{
			chapter: '-',
			name: 'Add',
			id: 'test-add',
			path: '../test_add.py'
		},
		{
			chapter: '-',
			name: 'Callback',
			id: 'test-callback',
			path: '../test_callback.py'
		},
		{
			chapter: '-',
			name: 'Fibonacci',
			id: 'test-fibonacci',
			path: '../test_fibonacci.py'
		},
		{
			chapter: '-',
			name: 'For loop',
			id: 'test-for',
			path: '../test_for.py'
		},
		{
			chapter: '-',
			name: 'If-Else',
			id: 'test-ifelse',
			path: '../test_ifelse.py'
		},
		{
			chapter: '-',
			name: 'Intrinsics',
			id: 'test-intrinsics',
			path: '../test_intrinsics.py'
		},
		{
			chapter: '-',
			name: 'Is prime',
			id: 'test-is-prime',
			path: '../test_is_prime.py'
		},
		{
			chapter: '-',
			name: 'noreturn',
			id: 'test-noreturn',
			path: '../test_noreturn.py'
		},
		{
			chapter: '-',
			name: 'Unary',
			id: 'test-unary',
			path: '../test_unary.py'
		},
		{
			chapter: '-',
			name: 'While (nested)',
			id: 'test-while-nested',
			path: '../test_while_nested.py'
		},
		{
			chapter: '-',
			name: 'While',
			id: 'test-while',
			path: '../test_while.py'
		},
	];

	if (typeof exports !== 'undefined') {
		exports.PLAY_SAMPLES = PLAY_SAMPLES;
	} else {
		self.PLAY_SAMPLES = PLAY_SAMPLES;
	}
})();
