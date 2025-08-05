-- Backup generado por Gym Manager
SET FOREIGN_KEY_CHECKS=0;

-- Estructura de la tabla alembic_version
CREATE TABLE IF NOT EXISTS `alembic_version` (
  `version_num` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Datos de la tabla alembic_version
INSERT INTO `alembic_version` (`version_num`) VALUES ('432e11afa4ba');

-- Estructura de la tabla comprobantes_pago
CREATE TABLE IF NOT EXISTS `comprobantes_pago` (
  `id_comprobante` int NOT NULL AUTO_INCREMENT,
  `contenido` blob NOT NULL,
  `fecha_emision` datetime NOT NULL,
  `id_pago` int NOT NULL,
  PRIMARY KEY (`id_comprobante`),
  UNIQUE KEY `id_pago` (`id_pago`),
  CONSTRAINT `comprobantes_pago_ibfk_1` FOREIGN KEY (`id_pago`) REFERENCES `pagos` (`id_pago`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de la tabla comprobantes_pago
INSERT INTO `comprobantes_pago` (`id_comprobante`, `contenido`, `fecha_emision`, `id_pago`) VALUES (1, 'Q29tcHJvYmFudGUgZGUgZWplbXBsbw==', '2025-06-17 18:06:58', 1);
INSERT INTO `comprobantes_pago` (`id_comprobante`, `contenido`, `fecha_emision`, `id_pago`) VALUES (2, 'JVBERi0xLjQKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tCjEgMCBvYmoKPDwKL0YxIDIgMCBSIC9GMiAzIDAgUgo+PgplbmRvYmoKMiAwIG9iago8PAovQmFzZUZvbnQgL0hlbHZldGljYSAvRW5jb2RpbmcgL1dpbkFuc2lFbmNvZGluZyAvTmFtZSAvRjEgL1N1YnR5cGUgL1R5cGUxIC9UeXBlIC9Gb250Cj4+CmVuZG9iagozIDAgb2JqCjw8Ci9CYXNlRm9udCAvSGVsdmV0aWNhLUJvbGQgL0VuY29kaW5nIC9XaW5BbnNpRW5jb2RpbmcgL05hbWUgL0YyIC9TdWJ0eXBlIC9UeXBlMSAvVHlwZSAvRm9udAo+PgplbmRvYmoKNCAwIG9iago8PAovQ29udGVudHMgOCAwIFIgL01lZGlhQm94IFsgMCAwIDYxMiA3OTIgXSAvUGFyZW50IDcgMCBSIC9SZXNvdXJjZXMgPDwKL0ZvbnQgMSAwIFIgL1Byb2NTZXQgWyAvUERGIC9UZXh0IC9JbWFnZUIgL0ltYWdlQyAvSW1hZ2VJIF0KPj4gL1JvdGF0ZSAwIC9UcmFucyA8PAoKPj4gCiAgL1R5cGUgL1BhZ2UKPj4KZW5kb2JqCjUgMCBvYmoKPDwKL1BhZ2VNb2RlIC9Vc2VOb25lIC9QYWdlcyA3IDAgUiAvVHlwZSAvQ2F0YWxvZwo+PgplbmRvYmoKNiAwIG9iago8PAovQXV0aG9yIChcKGFub255bW91c1wpKSAvQ3JlYXRpb25EYXRlIChEOjIwMjUwNjE3MTk1MzU4LTAzJzAwJykgL0NyZWF0b3IgKFwodW5zcGVjaWZpZWRcKSkgL0tleXdvcmRzICgpIC9Nb2REYXRlIChEOjIwMjUwNjE3MTk1MzU4LTAzJzAwJykgL1Byb2R1Y2VyIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgCiAgL1N1YmplY3QgKFwodW5zcGVjaWZpZWRcKSkgL1RpdGxlIChcKGFub255bW91c1wpKSAvVHJhcHBlZCAvRmFsc2UKPj4KZW5kb2JqCjcgMCBvYmoKPDwKL0NvdW50IDEgL0tpZHMgWyA0IDAgUiBdIC9UeXBlIC9QYWdlcwo+PgplbmRvYmoKOCAwIG9iago8PAovRmlsdGVyIFsgL0FTQ0lJODVEZWNvZGUgL0ZsYXRlRGVjb2RlIF0gL0xlbmd0aCA1NzEKPj4Kc3RyZWFtCkdhdG4jaGJTa1kmQkVdKC8rMTRZMjs3XnE+S1lnUFcvOHA/KyRCRDpbVmlBWjpwVDwibWhPUTlEKzUySiZFcjYxajI4PnJITy0sb0NuS2AjaSVmciQlMD9tWFZMWGgkYVI4IkpNYHI/V1JCX0psUUJZJl02XC5rLV5nYUkqJlxxcjohYmMwWEpUL1JsLVg5NU4hQ0FpTyYuWFUyPV9dNSxCK204PVdsdC42KnAociNfU2o8JDUtJUklUm1WPytrOFRpTWspJDVNOCh0PjFxUHF1OnB0bjdjUVlia2RBQ0NeQUwkPDxpO1UjbCxETkVWcmdlKXNOS0otLz9dcGA/Xy9ibys3WWlWZ19MTEQ/amE0bUQ/Xy1cbCsmalI3c1pEY11kLkI3Q1hTaEdFJjRjS2cqbm8qbWkvYDRJQ2EnXltcSDZCXm8jQk5GbUQnZUxfXE9SWidqW2JxXmM1R2RNWlI4SVtta24uVVg9Ji9DXSlUOClNOllaZj81QjErIUlvNzhJQzwpLz1QPzVrclUoR2RwQWpYOmg5ZUJIUW0jNltfWTNiUDlASTdLbzJhPChtJU9aclp0ZHJHUSR1SWVdREVwSSksdUpvLlE5WWkuJmAhbCtwQzktIzFAMyJGSU1NIm1ScUYrP1tDRkM0IzVLJzQmND5DW2lORkJlUHEuJkVQIkJWWHVkaHBGaytrZlFBRDAlajMxUTRhX0BnLyJmcjRTP29oOVc6bWxJVGxrPWNxS11qQFY7RnQkfj5lbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA5CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDA3MyAwMDAwMCBuIAowMDAwMDAwMTE0IDAwMDAwIG4gCjAwMDAwMDAyMjEgMDAwMDAgbiAKMDAwMDAwMDMzMyAwMDAwMCBuIAowMDAwMDAwNTI2IDAwMDAwIG4gCjAwMDAwMDA1OTQgMDAwMDAgbiAKMDAwMDAwMDg3NyAwMDAwMCBuIAowMDAwMDAwOTM2IDAwMDAwIG4gCnRyYWlsZXIKPDwKL0lEIApbPGVkOTU1MWQ4NTQzMTYzNTY1NzBiMzA2NzFhOWRkYzFlPjxlZDk1NTFkODU0MzE2MzU2NTcwYjMwNjcxYTlkZGMxZT5dCiUgUmVwb3J0TGFiIGdlbmVyYXRlZCBQREYgZG9jdW1lbnQgLS0gZGlnZXN0IChodHRwOi8vd3d3LnJlcG9ydGxhYi5jb20pCgovSW5mbyA2IDAgUgovUm9vdCA1IDAgUgovU2l6ZSA5Cj4+CnN0YXJ0eHJlZgoxNTk3CiUlRU9GCg==', '2025-06-17 19:53:59', 7);
INSERT INTO `comprobantes_pago` (`id_comprobante`, `contenido`, `fecha_emision`, `id_pago`) VALUES (3, 'JVBERi0xLjQKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tCjEgMCBvYmoKPDwKL0YxIDIgMCBSIC9GMiAzIDAgUgo+PgplbmRvYmoKMiAwIG9iago8PAovQmFzZUZvbnQgL0hlbHZldGljYSAvRW5jb2RpbmcgL1dpbkFuc2lFbmNvZGluZyAvTmFtZSAvRjEgL1N1YnR5cGUgL1R5cGUxIC9UeXBlIC9Gb250Cj4+CmVuZG9iagozIDAgb2JqCjw8Ci9CYXNlRm9udCAvSGVsdmV0aWNhLUJvbGQgL0VuY29kaW5nIC9XaW5BbnNpRW5jb2RpbmcgL05hbWUgL0YyIC9TdWJ0eXBlIC9UeXBlMSAvVHlwZSAvRm9udAo+PgplbmRvYmoKNCAwIG9iago8PAovQ29udGVudHMgOCAwIFIgL01lZGlhQm94IFsgMCAwIDYxMiA3OTIgXSAvUGFyZW50IDcgMCBSIC9SZXNvdXJjZXMgPDwKL0ZvbnQgMSAwIFIgL1Byb2NTZXQgWyAvUERGIC9UZXh0IC9JbWFnZUIgL0ltYWdlQyAvSW1hZ2VJIF0KPj4gL1JvdGF0ZSAwIC9UcmFucyA8PAoKPj4gCiAgL1R5cGUgL1BhZ2UKPj4KZW5kb2JqCjUgMCBvYmoKPDwKL1BhZ2VNb2RlIC9Vc2VOb25lIC9QYWdlcyA3IDAgUiAvVHlwZSAvQ2F0YWxvZwo+PgplbmRvYmoKNiAwIG9iago8PAovQXV0aG9yIChcKGFub255bW91c1wpKSAvQ3JlYXRpb25EYXRlIChEOjIwMjUwNjE4MDkwMzU0LTAzJzAwJykgL0NyZWF0b3IgKFwodW5zcGVjaWZpZWRcKSkgL0tleXdvcmRzICgpIC9Nb2REYXRlIChEOjIwMjUwNjE4MDkwMzU0LTAzJzAwJykgL1Byb2R1Y2VyIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgCiAgL1N1YmplY3QgKFwodW5zcGVjaWZpZWRcKSkgL1RpdGxlIChcKGFub255bW91c1wpKSAvVHJhcHBlZCAvRmFsc2UKPj4KZW5kb2JqCjcgMCBvYmoKPDwKL0NvdW50IDEgL0tpZHMgWyA0IDAgUiBdIC9UeXBlIC9QYWdlcwo+PgplbmRvYmoKOCAwIG9iago8PAovRmlsdGVyIFsgL0FTQ0lJODVEZWNvZGUgL0ZsYXRlRGVjb2RlIF0gL0xlbmd0aCA1ODcKPj4Kc3RyZWFtCkdhdG4jOW9uIV4mO0taTCdtJlNJR0xcUSxOcFNnXWcvVz9uV2czOSZhJ1EmWkJGbWFLUUUjR0xqMj9aUDxAXGR1ImNsdCM6WXRXXiYwTzNlczM+QTBOcy81RiN0UkNmISljLUxuSEQpa2FjRCpBQW5pR10nZHA9Nzg8UGtrTF9SOCkmcW5EVCE4VEQ9JkZKLFpOMm1nSTVxM0QyZFVQazJhSz1JdEBMY0lgRDgjMmZmPFgnalFvZk9EUWdIWEUuayM7bnApb1JUNFJtTE5hT29Acz1PZFU0cm5EKUdQOmFQPEQ+S29IWWRkN21ERDVTYW5Nak0xLmdcaW9fWkdoXzIlMjpUaTJhJkhYJ2BKXilAUExkbSNyV0pyZHNbJSNsNjZZV3MwV1dXZ1FrVkVdckVRQmlKUWZeTlskUWpWXXJZTD9vJmY3JiYwSUYzJzQ6OSIqIjxOLSxQbkdQWEhIJEgua1U7ZyxEPi9fLjRGa0E8Pm1zKTBiK01tP1F0RDBgc2dtXWspVWlCIyNXa2NFVi47Jl8sJENBNmpgP04iXT9GcC5IaG4yJWhbNnMwL00mZmN0WSVtOWYrR1B1OWpYQCdATFFYNVsqVGVhbjJBbCZGdThrIyM/U1ZmPioqKDtgSzYwJy8nZ2VTLTZLMGYrUl8xMFJmbk9sWlU+dEFOUz8tJyc5TCtdOWFFbDFPaDFgZ2o2MilJci1dQUVkdD4lSTIiXWxOP1VmOUxhU2dgI25cJWtzVmIzbjghJjZjWGwsNlF1NzdQLF85bn4+ZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgOQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwNzMgMDAwMDAgbiAKMDAwMDAwMDExNCAwMDAwMCBuIAowMDAwMDAwMjIxIDAwMDAwIG4gCjAwMDAwMDAzMzMgMDAwMDAgbiAKMDAwMDAwMDUyNiAwMDAwMCBuIAowMDAwMDAwNTk0IDAwMDAwIG4gCjAwMDAwMDA4NzcgMDAwMDAgbiAKMDAwMDAwMDkzNiAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9JRCAKWzxkYjEwNmY3YWZhZmUyMTA0NzcyZTFhNTc4YjRhZTk3ZD48ZGIxMDZmN2FmYWZlMjEwNDc3MmUxYTU3OGI0YWU5N2Q+XQolIFJlcG9ydExhYiBnZW5lcmF0ZWQgUERGIGRvY3VtZW50IC0tIGRpZ2VzdCAoaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tKQoKL0luZm8gNiAwIFIKL1Jvb3QgNSAwIFIKL1NpemUgOQo+PgpzdGFydHhyZWYKMTYxMwolJUVPRgo=', '2025-06-18 09:03:54', 8);
INSERT INTO `comprobantes_pago` (`id_comprobante`, `contenido`, `fecha_emision`, `id_pago`) VALUES (4, 'JVBERi0xLjQKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tCjEgMCBvYmoKPDwKL0YxIDIgMCBSIC9GMiAzIDAgUgo+PgplbmRvYmoKMiAwIG9iago8PAovQmFzZUZvbnQgL0hlbHZldGljYSAvRW5jb2RpbmcgL1dpbkFuc2lFbmNvZGluZyAvTmFtZSAvRjEgL1N1YnR5cGUgL1R5cGUxIC9UeXBlIC9Gb250Cj4+CmVuZG9iagozIDAgb2JqCjw8Ci9CYXNlRm9udCAvSGVsdmV0aWNhLUJvbGQgL0VuY29kaW5nIC9XaW5BbnNpRW5jb2RpbmcgL05hbWUgL0YyIC9TdWJ0eXBlIC9UeXBlMSAvVHlwZSAvRm9udAo+PgplbmRvYmoKNCAwIG9iago8PAovQ29udGVudHMgOCAwIFIgL01lZGlhQm94IFsgMCAwIDYxMiA3OTIgXSAvUGFyZW50IDcgMCBSIC9SZXNvdXJjZXMgPDwKL0ZvbnQgMSAwIFIgL1Byb2NTZXQgWyAvUERGIC9UZXh0IC9JbWFnZUIgL0ltYWdlQyAvSW1hZ2VJIF0KPj4gL1JvdGF0ZSAwIC9UcmFucyA8PAoKPj4gCiAgL1R5cGUgL1BhZ2UKPj4KZW5kb2JqCjUgMCBvYmoKPDwKL1BhZ2VNb2RlIC9Vc2VOb25lIC9QYWdlcyA3IDAgUiAvVHlwZSAvQ2F0YWxvZwo+PgplbmRvYmoKNiAwIG9iago8PAovQXV0aG9yIChcKGFub255bW91c1wpKSAvQ3JlYXRpb25EYXRlIChEOjIwMjUwNjI1MTAzODUyLTAzJzAwJykgL0NyZWF0b3IgKFwodW5zcGVjaWZpZWRcKSkgL0tleXdvcmRzICgpIC9Nb2REYXRlIChEOjIwMjUwNjI1MTAzODUyLTAzJzAwJykgL1Byb2R1Y2VyIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgCiAgL1N1YmplY3QgKFwodW5zcGVjaWZpZWRcKSkgL1RpdGxlIChcKGFub255bW91c1wpKSAvVHJhcHBlZCAvRmFsc2UKPj4KZW5kb2JqCjcgMCBvYmoKPDwKL0NvdW50IDEgL0tpZHMgWyA0IDAgUiBdIC9UeXBlIC9QYWdlcwo+PgplbmRvYmoKOCAwIG9iago8PAovRmlsdGVyIFsgL0FTQ0lJODVEZWNvZGUgL0ZsYXRlRGVjb2RlIF0gL0xlbmd0aCA1NzAKPj4Kc3RyZWFtCkdhdG4jaGJWKkMmQkVdJj01OEU9QzoqV0VbT10iaTslb15dNVBGOzZKViJIQWlCbFA9bXJgRFNKQy1kKzE0JmNhcSE8QDpwKDAyaGZfZ2E6SkVuMiRHNmZUPlQpX0oxK2IsMSI0U19aKUE+VTlOPClQSmMkakEtOiNGOUNBTXVZMVwrJF90YCNfWyFlLS9mMTQkUDphPUwlJjMvYVNKQlNvNl50RTJjWyxhWC5fK0glYFQhTW1CZXAsSGssczQ+XSssOVJoclpFKiwza11sRGRJL2lkXmhWSUJvUE5PXEhxSSVPVT9GbFlFKChGRV9SUG85RnRFTTlxbmpdcGA/XyhPWic5RjJiQWQjLWVgXmolV0ZpaSVHb1hNNGduaDBlOzRuU3M/KShkT21TbiItIVpFbkYsL3JfXUUyQUAiZGZiaCVPJWxVSCwtZ1ZOWSNqM2hWT2JFaFkwR2tEXSMtZm9yO0BwUldqPjxUPlFIaD5eW2dgOCZwYlwkQU8lZExHcCM5akkoIShFTi5VKWpJYTlHUS1NYGNvazBsK11nLDBtZVY2Kk8yJzZOWStYaC43TE9IVmU+UjQ3aDQ0MydyXWE5JlcpQyEnXFZWZSk7OV9LPy4+U206T0IvLUxlYmhEckR0N1trZSclYUdPa0pVSG5aIUA1bU80KkQ5ZUciI0dOWWA7YSE2MmhvR3JwI1JKOkpXOjBtKyE5NytvOD91dD4rYT9hUEY4bzFBOlFPcCNALGk/KU44WWN+PmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDkKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDczIDAwMDAwIG4gCjAwMDAwMDAxMTQgMDAwMDAgbiAKMDAwMDAwMDIyMSAwMDAwMCBuIAowMDAwMDAwMzMzIDAwMDAwIG4gCjAwMDAwMDA1MjYgMDAwMDAgbiAKMDAwMDAwMDU5NCAwMDAwMCBuIAowMDAwMDAwODc3IDAwMDAwIG4gCjAwMDAwMDA5MzYgMDAwMDAgbiAKdHJhaWxlcgo8PAovSUQgCls8YjdmMWI5ZDYzMWIyZDRmZmFjYWYzMGM4ZjFjNjliZTY+PGI3ZjFiOWQ2MzFiMmQ0ZmZhY2FmMzBjOGYxYzY5YmU2Pl0KJSBSZXBvcnRMYWIgZ2VuZXJhdGVkIFBERiBkb2N1bWVudCAtLSBkaWdlc3QgKGh0dHA6Ly93d3cucmVwb3J0bGFiLmNvbSkKCi9JbmZvIDYgMCBSCi9Sb290IDUgMCBSCi9TaXplIDkKPj4Kc3RhcnR4cmVmCjE1OTYKJSVFT0YK', '2025-06-25 10:38:52', 9);
INSERT INTO `comprobantes_pago` (`id_comprobante`, `contenido`, `fecha_emision`, `id_pago`) VALUES (5, 'JVBERi0xLjQKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tCjEgMCBvYmoKPDwKL0YxIDIgMCBSIC9GMiAzIDAgUgo+PgplbmRvYmoKMiAwIG9iago8PAovQmFzZUZvbnQgL0hlbHZldGljYSAvRW5jb2RpbmcgL1dpbkFuc2lFbmNvZGluZyAvTmFtZSAvRjEgL1N1YnR5cGUgL1R5cGUxIC9UeXBlIC9Gb250Cj4+CmVuZG9iagozIDAgb2JqCjw8Ci9CYXNlRm9udCAvSGVsdmV0aWNhLUJvbGQgL0VuY29kaW5nIC9XaW5BbnNpRW5jb2RpbmcgL05hbWUgL0YyIC9TdWJ0eXBlIC9UeXBlMSAvVHlwZSAvRm9udAo+PgplbmRvYmoKNCAwIG9iago8PAovQ29udGVudHMgOCAwIFIgL01lZGlhQm94IFsgMCAwIDYxMiA3OTIgXSAvUGFyZW50IDcgMCBSIC9SZXNvdXJjZXMgPDwKL0ZvbnQgMSAwIFIgL1Byb2NTZXQgWyAvUERGIC9UZXh0IC9JbWFnZUIgL0ltYWdlQyAvSW1hZ2VJIF0KPj4gL1JvdGF0ZSAwIC9UcmFucyA8PAoKPj4gCiAgL1R5cGUgL1BhZ2UKPj4KZW5kb2JqCjUgMCBvYmoKPDwKL1BhZ2VNb2RlIC9Vc2VOb25lIC9QYWdlcyA3IDAgUiAvVHlwZSAvQ2F0YWxvZwo+PgplbmRvYmoKNiAwIG9iago8PAovQXV0aG9yIChcKGFub255bW91c1wpKSAvQ3JlYXRpb25EYXRlIChEOjIwMjUwODA1MTc1NDQ0LTAzJzAwJykgL0NyZWF0b3IgKFwodW5zcGVjaWZpZWRcKSkgL0tleXdvcmRzICgpIC9Nb2REYXRlIChEOjIwMjUwODA1MTc1NDQ0LTAzJzAwJykgL1Byb2R1Y2VyIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgCiAgL1N1YmplY3QgKFwodW5zcGVjaWZpZWRcKSkgL1RpdGxlIChcKGFub255bW91c1wpKSAvVHJhcHBlZCAvRmFsc2UKPj4KZW5kb2JqCjcgMCBvYmoKPDwKL0NvdW50IDEgL0tpZHMgWyA0IDAgUiBdIC9UeXBlIC9QYWdlcwo+PgplbmRvYmoKOCAwIG9iago8PAovRmlsdGVyIFsgL0FTQ0lJODVEZWNvZGUgL0ZsYXRlRGVjb2RlIF0gL0xlbmd0aCA1NzEKPj4Kc3RyZWFtCkdhdG4jOyw+JV8mQkVdJi5JUCJXMixcYStnRC9TcFcvOG5pRkg9LUUtb2YoJT8mM3JYWT9NQTpOJF5sV1hkPU5VXlxyTHAldFcyYGMjWmJfPmMjZl43NmduPCRyQVxja2xdXzpkNzhqUjFZLlorUCovQ0gtckIuL1lhP3FOIj5IN1IhOiJodCtDKTciS0lbPFo1WSkrcV9JNjpjKV0yMDxrbkhtclg1XmdxYGBdalgwWF5EN2MpV1drKFFiNFVEXyUlLE45SnU5VWVUbUpYIiJSOXM2Wy43YWJGXCUySTAtYFIlNmBgVFFybE5oNkM3Uj5EWSJxbi0vKlk8dGU5PiJlUyFAW01bV0gwSiVuSkdgcmdxcF4+KS0hcEZaLmo8WnE9R3JhIihaWG5vOVRNYE5FcmlNYShBSSRsWyhwPF9qb0U/JnJCRlpKcldGVCMzJV1ILyNTPlpoQDNUTCROcDd1RWlddUNDXGVbLFpmcF0iOFduUmNBXFg4SzpiaWlkNzBjWldvOTlBQVsnaHFhck8qSXA0cXBOLyY0QiNtbzBZV0cmK2RJYyZlXUc1TkxnTHBtSE4+ZjBAVjQ1clptXz1UViMqa3BqYiJZXF0kPkxjdDgzdFYkSls/PSFYbGQzR3FpVm85UVVeamg3amBTImEvTjg7W1xHZWwxbU1IXWdoaStYbT5fSGE7ZnNwUy0vdGliMzRHYGQxWVFTZSQoRCMlUWpmNiI5IkFaKT8lUiFgJjpGWlZlNENcfj5lbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA5CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDA3MyAwMDAwMCBuIAowMDAwMDAwMTE0IDAwMDAwIG4gCjAwMDAwMDAyMjEgMDAwMDAgbiAKMDAwMDAwMDMzMyAwMDAwMCBuIAowMDAwMDAwNTI2IDAwMDAwIG4gCjAwMDAwMDA1OTQgMDAwMDAgbiAKMDAwMDAwMDg3NyAwMDAwMCBuIAowMDAwMDAwOTM2IDAwMDAwIG4gCnRyYWlsZXIKPDwKL0lEIApbPDE5MjZlMTdlNjdiYTZlMzVlZjU2YTA0M2JhNGYxNmI5PjwxOTI2ZTE3ZTY3YmE2ZTM1ZWY1NmEwNDNiYTRmMTZiOT5dCiUgUmVwb3J0TGFiIGdlbmVyYXRlZCBQREYgZG9jdW1lbnQgLS0gZGlnZXN0IChodHRwOi8vd3d3LnJlcG9ydGxhYi5jb20pCgovSW5mbyA2IDAgUgovUm9vdCA1IDAgUgovU2l6ZSA5Cj4+CnN0YXJ0eHJlZgoxNTk3CiUlRU9GCg==', '2025-08-05 17:54:44', 10);
INSERT INTO `comprobantes_pago` (`id_comprobante`, `contenido`, `fecha_emision`, `id_pago`) VALUES (6, 'JVBERi0xLjQKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tCjEgMCBvYmoKPDwKL0YxIDIgMCBSIC9GMiAzIDAgUgo+PgplbmRvYmoKMiAwIG9iago8PAovQmFzZUZvbnQgL0hlbHZldGljYSAvRW5jb2RpbmcgL1dpbkFuc2lFbmNvZGluZyAvTmFtZSAvRjEgL1N1YnR5cGUgL1R5cGUxIC9UeXBlIC9Gb250Cj4+CmVuZG9iagozIDAgb2JqCjw8Ci9CYXNlRm9udCAvSGVsdmV0aWNhLUJvbGQgL0VuY29kaW5nIC9XaW5BbnNpRW5jb2RpbmcgL05hbWUgL0YyIC9TdWJ0eXBlIC9UeXBlMSAvVHlwZSAvRm9udAo+PgplbmRvYmoKNCAwIG9iago8PAovQ29udGVudHMgOCAwIFIgL01lZGlhQm94IFsgMCAwIDYxMiA3OTIgXSAvUGFyZW50IDcgMCBSIC9SZXNvdXJjZXMgPDwKL0ZvbnQgMSAwIFIgL1Byb2NTZXQgWyAvUERGIC9UZXh0IC9JbWFnZUIgL0ltYWdlQyAvSW1hZ2VJIF0KPj4gL1JvdGF0ZSAwIC9UcmFucyA8PAoKPj4gCiAgL1R5cGUgL1BhZ2UKPj4KZW5kb2JqCjUgMCBvYmoKPDwKL1BhZ2VNb2RlIC9Vc2VOb25lIC9QYWdlcyA3IDAgUiAvVHlwZSAvQ2F0YWxvZwo+PgplbmRvYmoKNiAwIG9iago8PAovQXV0aG9yIChcKGFub255bW91c1wpKSAvQ3JlYXRpb25EYXRlIChEOjIwMjUwODA1MTc1NTIwLTAzJzAwJykgL0NyZWF0b3IgKFwodW5zcGVjaWZpZWRcKSkgL0tleXdvcmRzICgpIC9Nb2REYXRlIChEOjIwMjUwODA1MTc1NTIwLTAzJzAwJykgL1Byb2R1Y2VyIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgCiAgL1N1YmplY3QgKFwodW5zcGVjaWZpZWRcKSkgL1RpdGxlIChcKGFub255bW91c1wpKSAvVHJhcHBlZCAvRmFsc2UKPj4KZW5kb2JqCjcgMCBvYmoKPDwKL0NvdW50IDEgL0tpZHMgWyA0IDAgUiBdIC9UeXBlIC9QYWdlcwo+PgplbmRvYmoKOCAwIG9iago8PAovRmlsdGVyIFsgL0FTQ0lJODVEZWNvZGUgL0ZsYXRlRGVjb2RlIF0gL0xlbmd0aCA1NzYKPj4Kc3RyZWFtCkdhdG4jOWknZScmO0taTCdtJjo1THE1QyZtQzlqcywhXEssJmcnLiUtKyVQS1coR1g/PjVnX0dgJUdiXjViXzhDR2s/PVFqUnBHNCFwIzlOa0giYVtSRFxmZ0owYTFgKz0uYF9eWWdTO3Jacjc2O1pnMSYzMTJXaVAtZ1gtODVXU0E2KWAhNGNuNXQ5ZD1zZW4+ZkMoVztMLEwyKl9WQy9gJSVBKWtBWWIjPCVpK1s8N0dbZ0VzSHAuWjhtUjgpPWhoY0QuVSNCSGJRcC4pO0AuaVduTiFDWUM0dGNnJSk4dVZAUWk4TXQ5PjEkdF1xKCpXKSx0USVUZGw6bllYTiVFIi0zbkVLRGk8RFJIZk49NF0tbSNpUUk1L0RKNyJUPV1oQUlXaiM9alA2V0BRISdhQk4vSF1eTlFydWA7cWshIzBlIlA9SkY7OEYzJzJELShCNC81VEtzZzZzaCgyNVdrSnVBVUFjUjtHSEloaFNjUG5JQi5wRFs7YEhwcTdlckxZTzhuMkRXK2Q+Z1pZPGZoNFs6P0ozUzdlSHA5IXFaRFdwcEdDNnBabC49MSpYOCRmMWQwXnBWMi86bWcwVzFRIUohNitTLlJ0RW1ELGBOUUMqblNTNi5FRHFvR1J0SmsuPzNFT3JyX05tZT5JcmI0YVBMPSxkVyo3akNfOlFYRkldRDMoXmNOV2YnaGw9QDxEakBASTdsIlxmY11bYmRFOnJgWUNQWUpRVzhwa1FHNlVHSVRPTHRWbGYxP2t+PmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDkKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDczIDAwMDAwIG4gCjAwMDAwMDAxMTQgMDAwMDAgbiAKMDAwMDAwMDIyMSAwMDAwMCBuIAowMDAwMDAwMzMzIDAwMDAwIG4gCjAwMDAwMDA1MjYgMDAwMDAgbiAKMDAwMDAwMDU5NCAwMDAwMCBuIAowMDAwMDAwODc3IDAwMDAwIG4gCjAwMDAwMDA5MzYgMDAwMDAgbiAKdHJhaWxlcgo8PAovSUQgCls8ZjliZjM3MDMwYmVhNGZiMDk3NmVlNmIxZWM2NWI3ZDI+PGY5YmYzNzAzMGJlYTRmYjA5NzZlZTZiMWVjNjViN2QyPl0KJSBSZXBvcnRMYWIgZ2VuZXJhdGVkIFBERiBkb2N1bWVudCAtLSBkaWdlc3QgKGh0dHA6Ly93d3cucmVwb3J0bGFiLmNvbSkKCi9JbmZvIDYgMCBSCi9Sb290IDUgMCBSCi9TaXplIDkKPj4Kc3RhcnR4cmVmCjE2MDIKJSVFT0YK', '2025-08-05 17:55:21', 11);

-- Estructura de la tabla cuota_mensual
CREATE TABLE IF NOT EXISTS `cuota_mensual` (
  `id_cuota` int NOT NULL AUTO_INCREMENT,
  `monto` float NOT NULL,
  `fecha_actualizacion` datetime NOT NULL,
  `activo` int DEFAULT NULL,
  PRIMARY KEY (`id_cuota`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de la tabla cuota_mensual
INSERT INTO `cuota_mensual` (`id_cuota`, `monto`, `fecha_actualizacion`, `activo`) VALUES (1, 5000.0, '2025-06-17 18:06:58', 1);

-- Estructura de la tabla metodos_pago
CREATE TABLE IF NOT EXISTS `metodos_pago` (
  `id_metodo_pago` int NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(50) NOT NULL,
  `estado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id_metodo_pago`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de la tabla metodos_pago
INSERT INTO `metodos_pago` (`id_metodo_pago`, `descripcion`, `estado`) VALUES (1, 'Efectivo', 1);
INSERT INTO `metodos_pago` (`id_metodo_pago`, `descripcion`, `estado`) VALUES (2, 'Tarjeta', 1);

-- Estructura de la tabla miembro_rutina
CREATE TABLE IF NOT EXISTS `miembro_rutina` (
  `id_miembro` int NOT NULL,
  `id_rutina` int NOT NULL,
  PRIMARY KEY (`id_miembro`,`id_rutina`),
  KEY `id_rutina` (`id_rutina`),
  CONSTRAINT `miembro_rutina_ibfk_1` FOREIGN KEY (`id_miembro`) REFERENCES `miembros` (`id_miembro`),
  CONSTRAINT `miembro_rutina_ibfk_2` FOREIGN KEY (`id_rutina`) REFERENCES `rutinas` (`id_rutina`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de la tabla miembro_rutina
INSERT INTO `miembro_rutina` (`id_miembro`, `id_rutina`) VALUES (1, 1);

-- Estructura de la tabla miembros
CREATE TABLE IF NOT EXISTS `miembros` (
  `id_miembro` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `apellido` varchar(50) NOT NULL,
  `documento` varchar(20) NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `genero` varchar(10) NOT NULL,
  `correo_electronico` varchar(100) NOT NULL,
  `estado` tinyint(1) NOT NULL,
  `tipo_membresia` varchar(20) NOT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `fecha_registro` datetime NOT NULL,
  `informacion_medica` text,
  `id_rutina` int DEFAULT NULL,
  PRIMARY KEY (`id_miembro`),
  UNIQUE KEY `documento` (`documento`),
  UNIQUE KEY `correo_electronico` (`correo_electronico`),
  KEY `fk_miembro_rutina` (`id_rutina`),
  CONSTRAINT `fk_miembro_rutina` FOREIGN KEY (`id_rutina`) REFERENCES `rutinas` (`id_rutina`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de la tabla miembros
INSERT INTO `miembros` (`id_miembro`, `nombre`, `apellido`, `documento`, `fecha_nacimiento`, `genero`, `correo_electronico`, `estado`, `tipo_membresia`, `direccion`, `telefono`, `fecha_registro`, `informacion_medica`, `id_rutina`) VALUES (1, 'Admin', 'Principal', '00000000', '1990-01-01', 'Otro', 'admin@gym.com', 1, 'Admin', 'Oficina', '123456789', '2025-06-17 18:06:58', 'Sin condiciones', 1);
INSERT INTO `miembros` (`id_miembro`, `nombre`, `apellido`, `documento`, `fecha_nacimiento`, `genero`, `correo_electronico`, `estado`, `tipo_membresia`, `direccion`, `telefono`, `fecha_registro`, `informacion_medica`, `id_rutina`) VALUES (2, 'Lucía', 'Gómez', '43011234', '1995-08-20', 'Femenino', 'lucia.gomez@email.com', 1, 'Premium', 'Av. Libertad 456', '3411234567', '2025-06-01 09:30:00', 'Sin restricciones', NULL);
INSERT INTO `miembros` (`id_miembro`, `nombre`, `apellido`, `documento`, `fecha_nacimiento`, `genero`, `correo_electronico`, `estado`, `tipo_membresia`, `direccion`, `telefono`, `fecha_registro`, `informacion_medica`, `id_rutina`) VALUES (3, 'Marcos', 'Fernández', '42111235', '1988-12-05', 'Masculino', 'marcos.fernandez@email.com', 1, 'Estándar', 'Calle 9 de Julio 789', '3412345678', '2025-06-02 11:00:00', 'Apto médico reciente', NULL);
INSERT INTO `miembros` (`id_miembro`, `nombre`, `apellido`, `documento`, `fecha_nacimiento`, `genero`, `correo_electronico`, `estado`, `tipo_membresia`, `direccion`, `telefono`, `fecha_registro`, `informacion_medica`, `id_rutina`) VALUES (4, 'Sofía', 'Rodríguez', '41011236', '1999-03-11', 'Femenino', 'sofia.rodriguez@email.com', 1, 'Básica', 'Pasaje Mitre 321', '3413456789', '2025-06-03 14:45:00', 'Asma leve controlada', NULL);
INSERT INTO `miembros` (`id_miembro`, `nombre`, `apellido`, `documento`, `fecha_nacimiento`, `genero`, `correo_electronico`, `estado`, `tipo_membresia`, `direccion`, `telefono`, `fecha_registro`, `informacion_medica`, `id_rutina`) VALUES (5, 'Carlos', 'López', '40011237', '1992-06-30', 'Masculino', 'carlos.lopez@email.com', 1, 'Premium', 'Av. San Martín 654', '3414567890', '2025-06-04 16:20:00', 'Hipertensión controlada', NULL);
INSERT INTO `miembros` (`id_miembro`, `nombre`, `apellido`, `documento`, `fecha_nacimiento`, `genero`, `correo_electronico`, `estado`, `tipo_membresia`, `direccion`, `telefono`, `fecha_registro`, `informacion_medica`, `id_rutina`) VALUES (6, 'Valentina', 'Martínez', '43111238', '2001-11-22', 'Femenino', 'valentina.martinez@email.com', 1, 'Estándar', 'Calle Belgrano 111', '3415678901', '2025-06-05 08:15:00', 'Ninguna', NULL);

-- Estructura de la tabla pagos
CREATE TABLE IF NOT EXISTS `pagos` (
  `id_pago` int NOT NULL AUTO_INCREMENT,
  `fecha_pago` datetime NOT NULL,
  `monto` float NOT NULL,
  `referencia` varchar(50) DEFAULT NULL,
  `estado` tinyint(1) NOT NULL,
  `id_miembro` int NOT NULL,
  `id_metodo_pago` int NOT NULL,
  PRIMARY KEY (`id_pago`),
  KEY `id_miembro` (`id_miembro`),
  KEY `id_metodo_pago` (`id_metodo_pago`),
  CONSTRAINT `pagos_ibfk_1` FOREIGN KEY (`id_miembro`) REFERENCES `miembros` (`id_miembro`),
  CONSTRAINT `pagos_ibfk_2` FOREIGN KEY (`id_metodo_pago`) REFERENCES `metodos_pago` (`id_metodo_pago`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de la tabla pagos
INSERT INTO `pagos` (`id_pago`, `fecha_pago`, `monto`, `referencia`, `estado`, `id_miembro`, `id_metodo_pago`) VALUES (1, '2025-06-17 18:06:58', 5000.0, 'Pago inicial', 1, 1, 1);
INSERT INTO `pagos` (`id_pago`, `fecha_pago`, `monto`, `referencia`, `estado`, `id_miembro`, `id_metodo_pago`) VALUES (2, '2025-06-17 00:00:00', 5000.0, 'aaa', 1, 1, 1);
INSERT INTO `pagos` (`id_pago`, `fecha_pago`, `monto`, `referencia`, `estado`, `id_miembro`, `id_metodo_pago`) VALUES (3, '2025-06-17 00:00:00', 5001.0, 'a', 0, 1, 1);
INSERT INTO `pagos` (`id_pago`, `fecha_pago`, `monto`, `referencia`, `estado`, `id_miembro`, `id_metodo_pago`) VALUES (4, '2025-06-17 00:00:00', 5000.0, 'aaa', 1, 1, 1);
INSERT INTO `pagos` (`id_pago`, `fecha_pago`, `monto`, `referencia`, `estado`, `id_miembro`, `id_metodo_pago`) VALUES (5, '2025-06-17 00:00:00', 5000.0, 'a', 1, 1, 1);
INSERT INTO `pagos` (`id_pago`, `fecha_pago`, `monto`, `referencia`, `estado`, `id_miembro`, `id_metodo_pago`) VALUES (6, '2025-06-17 00:00:00', 5000.0, 'a', 1, 1, 1);
INSERT INTO `pagos` (`id_pago`, `fecha_pago`, `monto`, `referencia`, `estado`, `id_miembro`, `id_metodo_pago`) VALUES (7, '2025-06-17 00:00:00', 5000.0, 'a', 1, 1, 1);
INSERT INTO `pagos` (`id_pago`, `fecha_pago`, `monto`, `referencia`, `estado`, `id_miembro`, `id_metodo_pago`) VALUES (8, '2025-06-18 00:00:00', 5000.0, 'pago mes de junio', 1, 1, 2);
INSERT INTO `pagos` (`id_pago`, `fecha_pago`, `monto`, `referencia`, `estado`, `id_miembro`, `id_metodo_pago`) VALUES (9, '2025-06-25 00:00:00', 5000.0, 'aaa', 1, 1, 2);
INSERT INTO `pagos` (`id_pago`, `fecha_pago`, `monto`, `referencia`, `estado`, `id_miembro`, `id_metodo_pago`) VALUES (10, '2025-08-05 00:00:00', 5000.0, '', 1, 1, 1);
INSERT INTO `pagos` (`id_pago`, `fecha_pago`, `monto`, `referencia`, `estado`, `id_miembro`, `id_metodo_pago`) VALUES (11, '2025-08-06 00:00:00', 5000.0, '', 1, 1, 1);

-- Estructura de la tabla rutinas
CREATE TABLE IF NOT EXISTS `rutinas` (
  `id_rutina` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `documento_rutina` longblob,
  `nivel_dificultad` varchar(20) NOT NULL,
  `fecha_creacion` datetime DEFAULT NULL,
  `fecha_horario` datetime DEFAULT NULL,
  PRIMARY KEY (`id_rutina`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de la tabla rutinas
INSERT INTO `rutinas` (`id_rutina`, `nombre`, `descripcion`, `documento_rutina`, `nivel_dificultad`, `fecha_creacion`, `fecha_horario`) VALUES (1, 'Rutina Básica', 'Rutina para principiantes', NULL, 'Intermedio', '2025-06-17 18:06:58', '2025-06-17 18:06:58');
INSERT INTO `rutinas` (`id_rutina`, `nombre`, `descripcion`, `documento_rutina`, `nivel_dificultad`, `fecha_creacion`, `fecha_horario`) VALUES (4, 'Rutina de pecho', 'Rutina de pecho', 'JVBERi0xLjQKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tCjEgMCBvYmoKPDwKL0YxIDIgMCBSIC9GMiAzIDAgUgo+PgplbmRvYmoKMiAwIG9iago8PAovQmFzZUZvbnQgL0hlbHZldGljYSAvRW5jb2RpbmcgL1dpbkFuc2lFbmNvZGluZyAvTmFtZSAvRjEgL1N1YnR5cGUgL1R5cGUxIC9UeXBlIC9Gb250Cj4+CmVuZG9iagozIDAgb2JqCjw8Ci9CYXNlRm9udCAvSGVsdmV0aWNhLUJvbGQgL0VuY29kaW5nIC9XaW5BbnNpRW5jb2RpbmcgL05hbWUgL0YyIC9TdWJ0eXBlIC9UeXBlMSAvVHlwZSAvRm9udAo+PgplbmRvYmoKNCAwIG9iago8PAovQ29udGVudHMgOCAwIFIgL01lZGlhQm94IFsgMCAwIDYxMiA3OTIgXSAvUGFyZW50IDcgMCBSIC9SZXNvdXJjZXMgPDwKL0ZvbnQgMSAwIFIgL1Byb2NTZXQgWyAvUERGIC9UZXh0IC9JbWFnZUIgL0ltYWdlQyAvSW1hZ2VJIF0KPj4gL1JvdGF0ZSAwIC9UcmFucyA8PAoKPj4gCiAgL1R5cGUgL1BhZ2UKPj4KZW5kb2JqCjUgMCBvYmoKPDwKL1BhZ2VNb2RlIC9Vc2VOb25lIC9QYWdlcyA3IDAgUiAvVHlwZSAvQ2F0YWxvZwo+PgplbmRvYmoKNiAwIG9iago8PAovQXV0aG9yIChcKGFub255bW91c1wpKSAvQ3JlYXRpb25EYXRlIChEOjIwMjUwODA1MTc1NDQ0LTAzJzAwJykgL0NyZWF0b3IgKFwodW5zcGVjaWZpZWRcKSkgL0tleXdvcmRzICgpIC9Nb2REYXRlIChEOjIwMjUwODA1MTc1NDQ0LTAzJzAwJykgL1Byb2R1Y2VyIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgCiAgL1N1YmplY3QgKFwodW5zcGVjaWZpZWRcKSkgL1RpdGxlIChcKGFub255bW91c1wpKSAvVHJhcHBlZCAvRmFsc2UKPj4KZW5kb2JqCjcgMCBvYmoKPDwKL0NvdW50IDEgL0tpZHMgWyA0IDAgUiBdIC9UeXBlIC9QYWdlcwo+PgplbmRvYmoKOCAwIG9iago8PAovRmlsdGVyIFsgL0FTQ0lJODVEZWNvZGUgL0ZsYXRlRGVjb2RlIF0gL0xlbmd0aCA1NzEKPj4Kc3RyZWFtCkdhdG4jOyw+JV8mQkVdJi5JUCJXMixcYStnRC9TcFcvOG5pRkg9LUUtb2YoJT8mM3JYWT9NQTpOJF5sV1hkPU5VXlxyTHAldFcyYGMjWmJfPmMjZl43NmduPCRyQVxja2xdXzpkNzhqUjFZLlorUCovQ0gtckIuL1lhP3FOIj5IN1IhOiJodCtDKTciS0lbPFo1WSkrcV9JNjpjKV0yMDxrbkhtclg1XmdxYGBdalgwWF5EN2MpV1drKFFiNFVEXyUlLE45SnU5VWVUbUpYIiJSOXM2Wy43YWJGXCUySTAtYFIlNmBgVFFybE5oNkM3Uj5EWSJxbi0vKlk8dGU5PiJlUyFAW01bV0gwSiVuSkdgcmdxcF4+KS0hcEZaLmo8WnE9R3JhIihaWG5vOVRNYE5FcmlNYShBSSRsWyhwPF9qb0U/JnJCRlpKcldGVCMzJV1ILyNTPlpoQDNUTCROcDd1RWlddUNDXGVbLFpmcF0iOFduUmNBXFg4SzpiaWlkNzBjWldvOTlBQVsnaHFhck8qSXA0cXBOLyY0QiNtbzBZV0cmK2RJYyZlXUc1TkxnTHBtSE4+ZjBAVjQ1clptXz1UViMqa3BqYiJZXF0kPkxjdDgzdFYkSls/PSFYbGQzR3FpVm85UVVeamg3amBTImEvTjg7W1xHZWwxbU1IXWdoaStYbT5fSGE7ZnNwUy0vdGliMzRHYGQxWVFTZSQoRCMlUWpmNiI5IkFaKT8lUiFgJjpGWlZlNENcfj5lbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA5CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDA3MyAwMDAwMCBuIAowMDAwMDAwMTE0IDAwMDAwIG4gCjAwMDAwMDAyMjEgMDAwMDAgbiAKMDAwMDAwMDMzMyAwMDAwMCBuIAowMDAwMDAwNTI2IDAwMDAwIG4gCjAwMDAwMDA1OTQgMDAwMDAgbiAKMDAwMDAwMDg3NyAwMDAwMCBuIAowMDAwMDAwOTM2IDAwMDAwIG4gCnRyYWlsZXIKPDwKL0lEIApbPDE5MjZlMTdlNjdiYTZlMzVlZjU2YTA0M2JhNGYxNmI5PjwxOTI2ZTE3ZTY3YmE2ZTM1ZWY1NmEwNDNiYTRmMTZiOT5dCiUgUmVwb3J0TGFiIGdlbmVyYXRlZCBQREYgZG9jdW1lbnQgLS0gZGlnZXN0IChodHRwOi8vd3d3LnJlcG9ydGxhYi5jb20pCgovSW5mbyA2IDAgUgovUm9vdCA1IDAgUgovU2l6ZSA5Cj4+CnN0YXJ0eHJlZgoxNTk3CiUlRU9GCg==', 'Principiante', '2025-08-05 18:01:26', '2025-08-05 18:01:26');

-- Estructura de la tabla usuarios
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `apellido` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `rol` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contraseña` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `estado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Datos de la tabla usuarios
INSERT INTO `usuarios` (`id_usuario`, `nombre`, `apellido`, `rol`, `contraseña`, `estado`) VALUES (1, 'admin', 'Sistema', 'admin', '$2b$12$okMU9ReP51sxgc6soPP0SuDftnpVuyeQxdyKrjr8Z6zbv.ddbsF6O', 1);
INSERT INTO `usuarios` (`id_usuario`, `nombre`, `apellido`, `rol`, `contraseña`, `estado`) VALUES (2, 'juampi', 'soperez', 'Empleado', '1234', 1);
INSERT INTO `usuarios` (`id_usuario`, `nombre`, `apellido`, `rol`, `contraseña`, `estado`) VALUES (3, 'facu', 'abba', 'Empleado', '1234', 1);
INSERT INTO `usuarios` (`id_usuario`, `nombre`, `apellido`, `rol`, `contraseña`, `estado`) VALUES (4, 'yoel', 'junges', 'Empleado', '1234', 1);
INSERT INTO `usuarios` (`id_usuario`, `nombre`, `apellido`, `rol`, `contraseña`, `estado`) VALUES (5, 'Lucía', 'Gómez', 'empleado', 'lucia123', 1);
INSERT INTO `usuarios` (`id_usuario`, `nombre`, `apellido`, `rol`, `contraseña`, `estado`) VALUES (6, 'Marcos', 'Fernández', 'empleado', 'marcos123', 1);
INSERT INTO `usuarios` (`id_usuario`, `nombre`, `apellido`, `rol`, `contraseña`, `estado`) VALUES (7, 'Sofía', 'Rodríguez', 'administrador', 'sofia123', 1);
INSERT INTO `usuarios` (`id_usuario`, `nombre`, `apellido`, `rol`, `contraseña`, `estado`) VALUES (8, 'Carlos', 'López', 'empleado', 'carlos123', 1);
INSERT INTO `usuarios` (`id_usuario`, `nombre`, `apellido`, `rol`, `contraseña`, `estado`) VALUES (9, 'Valentina', 'Martínez', 'administrador', 'valen123', 1);

-- Fin del backup

