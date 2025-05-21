section .data
	list_a dq 5, 7
	list_a_len dq 2
	list1_b_str0 db "a", 0
	list1_b_str1 db "b", 0
	list1_b dq list1_b_str0, list1_b_str1
	list2_b_str0 db "c", 0
	list2_b_str1 db "d", 0
	list2_b dq list2_b_str0, list2_b_str1
	concat_list_b dq list1_b_str0, list1_b_str1, list2_b_str0, list2_b_str1
	concat_list_b_len dq 4
	open_bracket_b db "["
	comma_space db ", "
	close_bracket_b db "]"
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
	sub rsp, 48
;	------------------------

	mov rax, [rbp + 16]
	mov rax, [rax - 8]
	mov rax, [rax + 0*8]
	push rax
	mov rax, [rbp + 16]
	mov rax, [rax - 8]
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
	pop rax
	pop rbx
	add rax, rbx
	push rax
	mov [rbp - 16], rax

	; Performing + operation
	mov rax, [rbp - 8]
	mov rbx, [rbp - 16]
	add rax, rbx
	push rax
	mov [rbp - 24], rax

;	---Protocole de sortie---
	mov rsp, rbp
	pop rbp
	ret
;	------------------------


_start:
	; Allocating space for 5 variable(s) & 1 function(s)
	push rbp
	mov rbp, rsp
	sub rsp, 48


	; a = [5, 7]
	mov rax, list_a
	mov [rbp - 8], rax

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
	mov rsi, rax
	call print_str
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
	mov rsi, rax
	call print_str
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
	mov rax, 1
	mov [rbp - 24], rax
	mov rax, 2
	mov [rbp - 32], rax

;	---Stacking parameters---
	push rbp

;	---Calling the function---
	call f
;	---Popping parameters---
;	--------------------
	mov [rbp - 40], rax

	; print: parameter 1 (x)
	mov rax, [rbp - 40]
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