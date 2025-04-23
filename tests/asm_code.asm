section .data
	num_buffer times 32 db 0  ; Buffer for number conversion
	cst_1 dq 5
	cst_2 dq 10
	var_8 resq 1  ; variable resultat
	str_0 db "\n", 0
	str_0_len equ $ - str_0

section .text
	global _start

_start:

	; Exit program
	mov rax, 60
	xor rdi, rdi
	syscall

; EOF
