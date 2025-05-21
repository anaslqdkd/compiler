section .data
	str_a db "abc", 0
	str_b db "def", 0
	concat_str_c db "abcdef", 0
	list_d dq 1, 2
	list_d_len dq 2
	list_e_str0 db "a", 0
	list_e_str1 db "b", 0
	list_e dq list_e_str0, list_e_str1
	list_e_len dq 2
	list1_f dq 1, 2
	list2_f dq list_e_str0, list_e_str1
	concat_list_f dq 1, 2, list_e_str0, list_e_str1
	concat_list_f_len dq 4
	open_bracket_f db "["
	comma_space db ", "
	close_bracket_f db "]"
	list_g dq 0, 5
	list_g_len dq 2
	open_bracket_g db "["
	close_bracket_g db "]"
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
	; Allocating space for 7 variable(s) & 0 function(s)
	push rbp
	mov rbp, rsp
	sub rsp, 56

	mov rax, str_a
	mov [rbp - 8], rax
	mov rax, str_b
	mov [rbp - 16], rax
	; String concatenation: c = a + b = "abcdef"
	mov rax, concat_str_c
	mov [rbp - 24], rax

	; print: parameter 1 (c)
	mov rax, [rbp - 24]
	mov rsi, rax
	call print_str

	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall


	; print() - empty print statement
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall

	; d = [1, 2]
	mov rax, list_d
	mov [rbp - 32], rax

	; e = ["a", "b"]
	mov rax, list_e
	mov [rbp - 40], rax

	; Concatenation : f = liste concaténée
	mov rax, concat_list_f
	mov [rbp - 48], rax

	; print: parameter 1 (f)
	mov rax, [rbp - 48]

	; Affichage de la liste f
	mov rsi, rax
	mov rcx, [concat_list_f_len]
	mov rax, 1
	mov rdi, 1
	mov rdx, 1
	push rsi
	push rcx
	mov rsi, open_bracket_f
	syscall
	pop rcx
	pop rsi
	mov rdx, rcx

print_list_f_loop:
	test rcx, rcx
	jz print_list_f_end
	mov rax, [rsi]
	push rsi
	push rcx
	push rdx
	mov rbx, rdx
	sub rbx, rcx
	cmp rbx, 0
	jne skip_type_0_f
	call print_rax
	jmp print_list_f_loop_next
skip_type_0_f:
	cmp rbx, 1
	jne skip_type_1_f
	call print_rax
	jmp print_list_f_loop_next
skip_type_1_f:
	cmp rbx, 2
	jne skip_type_2_f
	mov rsi, rax
	call print_str
	jmp print_list_f_loop_next
skip_type_2_f:
	cmp rbx, 3
	jne skip_type_3_f
	mov rsi, rax
	call print_str
	jmp print_list_f_loop_next
skip_type_3_f:
	call print_rax
print_list_f_loop_next:
	pop rdx
	pop rcx
	pop rsi
	dec rcx
	test rcx, rcx
	jz print_list_f_loop_advance
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
print_list_f_loop_advance:
	add rsi, 8
	jmp print_list_f_loop
print_list_f_end:
	mov rax, 1
	mov rdi, 1
	mov rsi, close_bracket_f
	mov rdx, 1
	syscall

	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall


	; print() - empty print statement
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall

	; g = [a, 5]
	; Mise à jour de l'élément 0 avec la valeur de a
	mov rax, [rbp - 8]
	mov [list_g + 0], rax
	mov rax, list_g
	mov [rbp - 56], rax

	; print: parameter 1 (g)
	mov rax, [rbp - 56]

	; Affichage de la liste g
	mov rsi, rax
	mov rcx, [list_g_len]
	mov rax, 1
	mov rdi, 1
	mov rdx, 1
	push rsi
	push rcx
	mov rsi, open_bracket_g
	syscall
	pop rcx
	pop rsi
	mov rdx, rcx

print_list_g_loop:
	test rcx, rcx
	jz print_list_g_end
	mov rax, [rsi]
	push rsi
	push rcx
	push rdx
	mov rbx, rdx
	sub rbx, rcx
	cmp rbx, 0
	jne skip_type_0_g
	mov rsi, rax
	call print_str
	jmp print_list_g_loop_next
skip_type_0_g:
	cmp rbx, 1
	jne skip_type_1_g
	call print_rax
	jmp print_list_g_loop_next
skip_type_1_g:
	call print_rax
print_list_g_loop_next:
	pop rdx
	pop rcx
	pop rsi
	dec rcx
	test rcx, rcx
	jz print_list_g_loop_advance
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
print_list_g_loop_advance:
	add rsi, 8
	jmp print_list_g_loop
print_list_g_end:
	mov rax, 1
	mov rdi, 1
	mov rsi, close_bracket_g
	mov rdx, 1
	syscall

	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall


	; print() - empty print statement
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