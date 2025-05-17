	section .data
		newline db 0xA

	section .bss
		buffer resb 20


	section .text
		global _start
		global g


	;	---print_rax protocol---
	print_rax:
		mov rcx, buffer + 20
		mov rbx, 10

	.convert_loop:
		xor rdx, rdx
		div rbx
		add dl, '0'
		dec rcx
		mov [rcx], dl
		test rax, rax
		jnz .convert_loop

		; write result
		mov rax, 1
		mov rdi, 1
		mov rsi, rcx
		mov rdx, buffer + 20
		sub rdx, rcx
		syscall

		; newline
		mov rax, 1
		mov rdi, 1
		mov rsi, newline
		mov rdx, 1
		syscall
		ret
	;	--------------------

	; ---print_str protocol---
	print_str:
		xor rcx, rcx

	.find_len_str:
		mov al, [rsi + rcx]
		test al, al
		jz .len_found_str
		inc rcx
		jmp .find_len_str

	.len_found_str:
		mov rdx, rcx
		mov rax, 1
		mov rdi, 1
		syscall
		ret
	;	--------------------


	g:
	;	---Protocole d'entree---
		push rbp
		mov rbp, rsp
		sub rsp, 1
	;	------------------------

		mov rax, 1
		push rax

		; Performing + operation
		pop rax
		mov rax, [rbp + 8 + 8]
		add rax, rbx
		push rax
		pop rax
		mov rax, [rbp - 8]

		; Performing + operation
		mov rax, [rbp + 8 + 16]
		mov rax, [rbp - 8]
		add rax, rbx
		push rax
		pop rax
		mov rax, [rbp - 8]

	;	---Protocole de sortie---
		mov rsp, rbp
		pop rbp
		ret
	;	------------------------


	_start:
		; Allocating space for 3 local variables
		push rbp
		mov rbp, rsp
		sub rsp, 24

		mov rax, 5
		mov rax, [rbp - 8]

	;	---Stacking parameters---
	;	---1-th parameter---
		mov rax, [rbp - 8]
		push rax
	;	---2-th parameter---
		mov rax, 17
		push rax

	;	---Calling the function---
		call g
	;	---Popping parameters---
		pop rax
		pop rax
	;	--------------------
		mov [rbp - 16], rax

		; print(A)
		mov rax, [rbp - 16]
		call print_rax


	;	---End of program---
		mov rax, 60
		xor rdi, rdi 
		syscall
	;	--------------------


	; EOF