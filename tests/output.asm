section .data
	list1_a dq 1, 2
	list2_a_str0 db "abc", 0
	list2_a dq list2_a_str0, 4
	concat_list_a dq 0, 0, 0, 0	; 4 elements for concatenation
	newline db 0xA

section .bss
	buffer resb 20


section .text
	global _start


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


_start:
	; Allocating space for 2 local variables
	push rbp
	mov rbp, rsp
	sub rsp, 16

	; Concatenation : a = [1, 2, "abc", 4]
	mov rsi, list1_a
	mov rax, [rsi+0]
	mov [concat_list_a+0], rax
	mov rax, [rsi+8]
	mov [concat_list_a+8], rax

	mov rsi, list2_a
	mov rax, [rsi+0]
	mov [concat_list_a+16], rax
	mov rax, [rsi+8]
	mov [concat_list_a+24], rax

	mov rax, concat_list_a
	mov [rbp-8], rax

	; b = a[1]
	mov rax, [rbp-8]
	mov rax, [rax + 1*8]
	mov [rbp-16], rax

	; print(b)
	mov rax, [rbp-16]
	call print_rax


;	---End of program---
	mov rax, 60
	xor rdi, rdi 
	syscall
;	--------------------


; EOF