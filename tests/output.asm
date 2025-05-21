section .data
	mult_list_a dq 5, 7, 5, 7
	mult_list_a_len dq 4
	open_bracket_a db "["
	comma_space db ", "
	close_bracket_a db "]"
	list1_b_str1 db "a", 0
	list1_b dq 1, list1_b_str1
	list2_b_str1 db "b", 0
	list2_b dq 2, list2_b_str1
	concat_list_b dq 1, list1_b_str1, 2, list2_b_str1
	concat_list_b_len dq 4
	open_bracket_b db "["
	close_bracket_b db "]"
	str_str db "hello", 0
	space_char db " ", 0
	char_temp_6_1 db 0, 0
	list_tab dq 1, 2, 0
	list_tab_len dq 3
	open_bracket_tab db "["
	close_bracket_tab db "]"
	newline db 0xA
	minus_sign db "-"

section .bss
	buffer resb 20


section .text
	global _start
	global f


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


f:
;	---Protocole d'entree---
	push rbp
	mov rbp, rsp
;	------------------------


	;--------if 0------
	mov rcx, rbp
	mov rcx, [rcx]
	mov rax, [rcx - 48]
	push rax
	mov rcx, rbp
	mov rcx, [rcx]
	mov rax, [rcx - 56]
	push rax

	; Performing < operation
	pop rbx
	pop rax
	cmp rax, rbx
	mov rax, 0
	setl al
	push rax

	cmp rax, 1
	jne end_if_0_14

	;operations in if
	mov rcx, rbp
	mov rcx, [rcx]
	mov rax, [rcx - 8]
	mov rax, [rax + 0*8]
	push rax
	mov rcx, rbp
	mov rcx, [rcx]
	mov rax, [rcx - 8]
	mov rax, [rax + 1*8]
	push rax

	; Performing * operation
	pop rbx
	pop rax
	imul rax, rbx
	push rax
	mov [rbp - 8], rax
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
	pop rbx
	pop rax
	add rax, rbx
	push rax
	mov [rbp - 16], rax
	mov rax, [rbp - 8]
	push rax
	mov rax, [rbp - 16]
	push rax

	; Performing + operation
	pop rbx
	pop rax
	add rax, rbx
	push rax
	mov [rbp - 24], rax
end_if_0_14:

;	---Protocole de sortie---
	mov rsp, rbp
	pop rbp
	ret
;	------------------------


_start:
	; Allocating space for 8 variable(s) & 1 function(s)
	push rbp
	mov rbp, rsp
	sub rsp, 72

	; List multiplication: a = [5, 7] * 2
	mov rax, mult_list_a
	mov [rbp - 8], rax
	mov [rbp - 8], rax

	; print: parameter 1 (a)
	mov rax, [rbp - 8]

	; Affichage de la liste a
	mov rsi, rax
	mov rcx, [mult_list_a_len]
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
	call print_rax
	jmp print_list_a_loop_next
skip_type_2_a:
	cmp rbx, 3
	jne skip_type_3_a
	call print_rax
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

	; print: parameter 2 (a)
	mov rax, [rbp - 8]
	mov rax, [rax + 3*8]
	call print_rax

	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall


	; Concatenation : b = liste concaténée
	mov rax, concat_list_b
	mov [rbp - 16], rax

	; print: parameter 1 (b)
	mov rax, [rbp - 16]

	; Affichage de la liste b
	mov rsi, rax
	mov rcx, [concat_list_b_len]
	mov rax, 1
	mov rdi, 1
	mov rdx, 1
	push rsi
	push rcx
	mov rsi, open_bracket_b
	syscall
	pop rcx
	pop rsi
	mov rdx, rcx

print_list_b_loop:
	test rcx, rcx
	jz print_list_b_end
	mov rax, [rsi]
	push rsi
	push rcx
	push rdx
	mov rbx, rdx
	sub rbx, rcx
	cmp rbx, 0
	jne skip_type_0_b
	call print_rax
	jmp print_list_b_loop_next
skip_type_0_b:
	cmp rbx, 1
	jne skip_type_1_b
	mov rsi, rax
	call print_str
	jmp print_list_b_loop_next
skip_type_1_b:
	cmp rbx, 2
	jne skip_type_2_b
	call print_rax
	jmp print_list_b_loop_next
skip_type_2_b:
	cmp rbx, 3
	jne skip_type_3_b
	mov rsi, rax
	call print_str
	jmp print_list_b_loop_next
skip_type_3_b:
	call print_rax
print_list_b_loop_next:
	pop rdx
	pop rcx
	pop rsi
	dec rcx
	test rcx, rcx
	jz print_list_b_loop_advance
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
print_list_b_loop_advance:
	add rsi, 8
	jmp print_list_b_loop
print_list_b_end:
	mov rax, 1
	mov rdi, 1
	mov rsi, close_bracket_b
	mov rdx, 1
	syscall

	; print: parameter 2 (b)
	mov rax, [rbp - 16]
	mov rax, [rax + 2*8]
	call print_rax

	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall

	mov rax, str_str
	mov [rbp - 24], rax

	; print: parameter 1 (str)
	mov rax, [rbp - 24]
	mov rsi, rax
	call print_str
	mov rax, 1
	mov rdi, 1
	mov rsi, space_char
	mov rdx, 1
	syscall

	; print: parameter 2 (str)
	mov rax, [rbp - 24]
	movzx rax, byte [rax + 1]
	mov byte [char_temp_6_1], al
	mov rsi, char_temp_6_1
	mov rdx, 1
	mov rax, 1
	mov rdi, 1
	syscall

	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall

	mov rax, 10
	mov [rbp - 32], rax

	; tab = [1, 2, u]
	; Mise à jour de l'élément 2 avec la valeur de u
	mov rax, [rbp - 32]
	mov [list_tab + 16], rax
	mov rax, list_tab
	mov [rbp - 40], rax

	; print: parameter 1 (tab)
	mov rax, [rbp - 40]

	; Affichage de la liste tab
	mov rsi, rax
	mov rcx, [list_tab_len]
	mov rax, 1
	mov rdi, 1
	mov rdx, 1
	push rsi
	push rcx
	mov rsi, open_bracket_tab
	syscall
	pop rcx
	pop rsi
	mov rdx, rcx

print_list_tab_loop:
	test rcx, rcx
	jz print_list_tab_end
	mov rax, [rsi]
	push rsi
	push rcx
	push rdx
	mov rbx, rdx
	sub rbx, rcx
	cmp rbx, 0
	jne skip_type_0_tab
	call print_rax
	jmp print_list_tab_loop_next
skip_type_0_tab:
	cmp rbx, 1
	jne skip_type_1_tab
	call print_rax
	jmp print_list_tab_loop_next
skip_type_1_tab:
	cmp rbx, 2
	jne skip_type_2_tab
	call print_rax
	jmp print_list_tab_loop_next
skip_type_2_tab:
	call print_rax
print_list_tab_loop_next:
	pop rdx
	pop rcx
	pop rsi
	dec rcx
	test rcx, rcx
	jz print_list_tab_loop_advance
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
print_list_tab_loop_advance:
	add rsi, 8
	jmp print_list_tab_loop
print_list_tab_end:
	mov rax, 1
	mov rdi, 1
	mov rsi, close_bracket_tab
	mov rdx, 1
	syscall

	; print: parameter 2 (tab)
	mov rax, [rbp - 40]
	mov rax, [rax + 2*8]
	call print_rax

	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall

	mov rax, 1
	mov [rbp - 48], rax
	mov rax, 2
	mov [rbp - 56], rax

;	---Stacking parameters---
	push rbp

;	---Calling the function---
	call f
;	---Popping parameters---
;	--------------------
	mov [rbp - 64], rax

	; print: parameter 1 (x)
	mov rax, [rbp - 64]
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