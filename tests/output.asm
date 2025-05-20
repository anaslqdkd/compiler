section .data
	mult_list_a dq 1, 2, 3, 1, 2, 3
	mult_list_a_len dq 6
	list1_b dq 4, 5
	list2_b dq 6, 7
	concat_list_b dq 0, 0, 0, 0	; 4 elements for concatenation
	concat_list_b_len dq 4
	str_8 db "Résultat: ", 0
	space_char db " ", 0
	newline db 0xA
	minus_sign db "-"

section .bss
	buffer resb 20


section .text
	global _start


;	---print_rax protocol---
print_rax:
	test rax, rax
	jns .positive
	push rax
	mov rax, 1
	mov rdi, 1
	mov rsi, minus_sign
	mov rdx, 1
	syscall
	pop rax
	neg rax
.positive:
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


_start:
	; Allocating space for 3 variable(s) & 0 function(s)
	push rbp
	mov rbp, rsp
	sub rsp, 24

	; List multiplication: a = [1, 2, 3] * 2
	mov rax, mult_list_a
	mov [rbp - 8], rax
	mov [rbp - 8], rax

	; print: parameter 1 (a)
	mov rax, [rbp - 8]
	mov rax, [rax + 3*8]
	call print_rax


	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall
	; Concatenation : b = [4, 5, 6, 7]
	mov rsi, list1_b
	mov rax, [rsi]
	mov [concat_list_b], rax
	mov rax, [rsi+8]
	mov [concat_list_b+8], rax

	mov rsi, list2_b
	mov rax, [rsi]
	mov [concat_list_b+16], rax
	mov rax, [rsi+8]
	mov [concat_list_b+24], rax

	mov rax, concat_list_b
	mov [rbp - 16], rax

	; print: parameter 1 (b)
	mov rax, [rbp - 16]
	mov rax, [rax + 2*8]
	call print_rax


	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall
	mov rax, 1
	push rax
	mov rax, 2
	push rax
	mov rax, 3
	push rax

	; Performing * operation
	pop rbx
	pop rax
	imul rax, rbx
	push rax

	; Performing + operation
	pop rax
	pop rbx
	add rax, rbx
	push rax
	mov [rbp - 24], rax

	; print: parameter 1 ("Résultat: ")
	mov rax, 1
	mov rdi, 1
	mov rsi, str_8
	mov rdx, 10
	syscall
	mov rax, 1
	mov rdi, 1
	mov rsi, space_char
	mov rdx, 1
	syscall

	; print: parameter 2 (c)
	mov rax, [rbp - 24]
	call print_rax


	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall


;	---End of program---
	mov rax, 60
	xor rdi, rdi 
	syscall
;	--------------------


; EOF