section .data
	cst_1 dd 3
	cst_2 db "flk", 0
	cst_3 dd 1
	cst_4 dd 2
	cst_5 dd 10
	cst_6 dd 8
	cst_7 dd 0
	cst_8 dd 5


section .text
	global _start
	global sans_param
	global feur
	global main
	global fr


_start:
	mov dword [rbp+8], 3
	call sans_param
sans_param:

;	---Protocole d'entrée---
	push rbp
	mov rbp, rsp
;	------------------------

	mov rax, 1
	mov rdi, 1
	mov rsi, cst_2
	mov rdx, 4
	syscall


;	---Protocole de sortie---
	pop rbp
	ret
;	------------------------


feur:

;	---Protocole d'entrée---
	push rbp
	mov rbp, rsp
	sub rsp, 24
;	------------------------


	mov dword [rbp+8], 5

	mov dword [rbp+8], 1


;	---Protocole de sortie---
	pop rbp
	ret
;	------------------------


main:

;	---Protocole d'entrée---
	push rbp
	mov rbp, rsp
;	------------------------



;	---Protocole de sortie---
	pop rbp
	ret
;	------------------------


fr:

;	---Protocole d'entrée---
	push rbp
	mov rbp, rsp
	sub rsp, 4
;	------------------------

	call main


;	---Protocole de sortie---
	pop rbp
	ret
;	------------------------


; EOF