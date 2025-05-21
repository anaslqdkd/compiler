section .data
	list1_a dq 1, 2
	list2_a_str0 db "abc", 0
	list2_a_str1 db "x", 0
	list2_a dq list2_a_str0, list2_a_str1
	concat_list_a dq 0, 0, 0, 0	; 4 elements for concatenation
	concat_list_a_len dq 4
	open_bracket_a db "["
	comma_space db ", "
	close_bracket_a db "]"
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
	; Allocating space for 1 variable(s) & 0 function(s)
	push rbp
	mov rbp, rsp
	sub rsp, 8


	; Concatenation : a = [1, 2, "abc", "x"]
	mov rsi, list1_a
	mov rax, [rsi]
	mov [concat_list_a], rax
	mov rax, [rsi+8]
	mov [concat_list_a+8], rax

	mov rsi, list2_a
	mov rax, [rsi]
	mov [concat_list_a+16], rax
	mov rax, [rsi+8]
	mov [concat_list_a+24], rax

	mov rax, concat_list_a
	mov [rbp - 8], rax

	; print: parameter 1 (a)
	mov rax, [rbp - 8]

	; Affichage de la liste a
	mov rsi, rax
	mov rcx, [concat_list_a_len]
	mov rax, 1
	mov rdi, 1
	mov rdx, 1
	push rsi
	push rcx
	mov rsi, open_bracket_a
	syscall
	pop rcx
	pop rsi
	mov rdx, rcx

print_list_a_loop:
	test rcx, rcx
	jz print_list_a_end
	mov rax, [rsi]
	push rsi
	push rcx
	push rdx
	mov rbx, rdx
	sub rbx, rcx
	cmp rbx, 0
	jne skip_type_0_a
	call print_rax
	jmp print_list_a_loop_next
skip_type_0_a:
	cmp rbx, 1
	jne skip_type_1_a
	call print_rax
	jmp print_list_a_loop_next
skip_type_1_a:
	cmp rbx, 2
	jne skip_type_2_a
	mov rsi, rax
	call print_str
	jmp print_list_a_loop_next
skip_type_2_a:
	cmp rbx, 3
	jne skip_type_3_a
	mov rsi, rax
	call print_str
	jmp print_list_a_loop_next
skip_type_3_a:
	call print_rax
print_list_a_loop_next:
	pop rdx
	pop rcx
	pop rsi
	dec rcx
	test rcx, rcx
	jz print_list_a_loop_advance
	push rsi
	push rcx
	push rdx
	mov rax, 1
	mov rdi, 1
	mov rsi, comma_space
	mov rdx, 2
	syscall
	pop rdx
	pop rcx
	pop rsi
print_list_a_loop_advance:
	add rsi, 8
	jmp print_list_a_loop
print_list_a_end:
	mov rax, 1
	mov rdi, 1
	mov rsi, close_bracket_a
	mov rdx, 1
	syscall

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