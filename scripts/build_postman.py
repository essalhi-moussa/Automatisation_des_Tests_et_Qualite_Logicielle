#!/usr/bin/env python3
"""Genere la collection Postman v2.1 et les environnements dans postman/.

Utilite : garder une source lisible et eviter les erreurs d'echappement JSON a la main.
Usage   : python scripts/build_postman.py
"""
import json
import os
import uuid

OUT = os.path.join(os.path.dirname(__file__), "..", "postman")
os.makedirs(OUT, exist_ok=True)

SCHEMAS = {
    "usersList": {
        "type": "object",
        "required": ["page", "per_page", "total", "total_pages", "data"],
        "properties": {
            "page": {"type": "integer"},
            "per_page": {"type": "integer"},
            "total": {"type": "integer"},
            "total_pages": {"type": "integer"},
            "data": {"type": "array", "items": {
                "type": "object",
                "required": ["id", "email", "first_name", "last_name", "avatar"],
                "properties": {
                    "id": {"type": "integer"},
                    "email": {"type": "string"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "avatar": {"type": "string"},
                }}},
        },
    },
    "userSingle": {
        "type": "object",
        "required": ["data"],
        "properties": {"data": {
            "type": "object",
            "required": ["id", "email", "first_name", "last_name", "avatar"],
        }},
    },
    "created": {
        "type": "object",
        "required": ["name", "job", "id", "createdAt"],
        "properties": {"name": {"type": "string"}, "job": {"type": "string"},
                       "id": {"type": ["string", "integer"]}, "createdAt": {"type": "string"}},
    },
    "updated": {
        "type": "object",
        "required": ["name", "job", "updatedAt"],
        "properties": {"name": {"type": "string"}, "job": {"type": "string"}, "updatedAt": {"type": "string"}},
    },
    "token": {"type": "object", "required": ["token"], "properties": {"token": {"type": "string"}}},
    "error": {"type": "object", "required": ["error"], "properties": {"error": {"type": "string"}}},
}


def tests(lines):
    return {"listen": "test", "script": {"type": "text/javascript", "exec": lines}}


def prereq(lines):
    return {"listen": "prerequest", "script": {"type": "text/javascript", "exec": lines}}


def common(status, schema_key=None):
    lines = [
        "pm.test('Statut HTTP %s', function () { pm.response.to.have.status(%s); });" % (status, status),
        "pm.test('Temps de reponse < ' + pm.environment.get('maxResponseTime') + ' ms', function () {",
        "    pm.expect(pm.response.responseTime).to.be.below(Number(pm.environment.get('maxResponseTime')));",
        "});",
    ]
    if status != 204:
        lines.append("pm.test('Content-Type JSON', function () { pm.expect(pm.response.headers.get('Content-Type')).to.include('json'); });")
    if schema_key:
        lines += [
            "const schema = %s;" % json.dumps(SCHEMAS[schema_key]),
            "pm.test('Schema JSON valide', function () { pm.response.to.have.jsonSchema(schema); });",
        ]
    return lines


def request(name, method, path, body=None, events=None, query=None, description=""):
    url = {"raw": "{{baseUrl}}" + path, "host": ["{{baseUrl}}"], "path": [p for p in path.split("/") if p]}
    if query:
        url["query"] = [{"key": k, "value": v} for k, v in query.items()]
        url["raw"] += "?" + "&".join("%s=%s" % kv for kv in query.items())
    req = {
        "method": method,
        "header": [
            {"key": "x-api-key", "value": "{{apiKey}}"},
            {"key": "Content-Type", "value": "application/json"},
            {"key": "Accept", "value": "application/json"},
        ],
        "url": url,
        "description": description,
    }
    if body is not None:
        req["body"] = {"mode": "raw", "raw": json.dumps(body, indent=2),
                       "options": {"raw": {"language": "json"}}}
    return {"name": name, "event": events or [], "request": req, "response": []}


items = [
    request("API-01 GET liste des utilisateurs (page 2)", "GET", "/api/users", query={"page": "2"},
            description="Liste paginee : 6 utilisateurs sur la page 2.",
            events=[tests(common(200, "usersList") + [
                "const body = pm.response.json();",
                "pm.test('Pagination coherente (page 2, 6 par page)', function () {",
                "    pm.expect(body.page).to.eql(2);",
                "    pm.expect(body.per_page).to.eql(6);",
                "    pm.expect(body.data).to.have.lengthOf(6);",
                "});",
                "pm.test('Chaque email contient @', function () {",
                "    body.data.forEach(function (u) { pm.expect(u.email).to.include('@'); });",
                "});",
                "pm.collectionVariables.set('firstUserId', body.data[0].id);",
            ])]),
    request("API-02 GET un utilisateur (id 2)", "GET", "/api/users/2",
            events=[tests(common(200, "userSingle") + [
                "const u = pm.response.json().data;",
                "pm.test('Utilisateur Janet Weaver', function () {",
                "    pm.expect(u.id).to.eql(2);",
                "    pm.expect(u.first_name).to.eql('Janet');",
                "    pm.expect(u.last_name).to.eql('Weaver');",
                "});",
            ])]),
    request("API-03 GET utilisateur inexistant (id 23)", "GET", "/api/users/23",
            description="Cas negatif : 404 et corps JSON vide.",
            events=[tests([
                "pm.test('Statut HTTP 404', function () { pm.response.to.have.status(404); });",
                "pm.test('Corps vide {}', function () { pm.expect(pm.response.json()).to.eql({}); });",
                "pm.test('Temps de reponse < seuil', function () {",
                "    pm.expect(pm.response.responseTime).to.be.below(Number(pm.environment.get('maxResponseTime')));",
                "});",
            ])]),
    request("API-04 POST creation d'un utilisateur", "POST", "/api/users",
            body={"name": "{{userName}}", "job": "{{userJob}}"},
            description="Les donnees ne sont pas persistees par Reqres : seul l'echo est verifiable.",
            events=[
                prereq([
                    "// Jeu de donnees dynamique : nom unique a chaque execution",
                    "const suffix = Math.floor(Math.random() * 100000);",
                    "pm.variables.set('userName', 'testeur-' + suffix);",
                    "pm.variables.set('userJob', 'QA automation');",
                ]),
                tests(common(201, "created") + [
                    "const b = pm.response.json();",
                    "pm.test('Les donnees envoyees sont renvoyees', function () {",
                    "    pm.expect(b.name).to.eql(pm.variables.get('userName'));",
                    "    pm.expect(b.job).to.eql('QA automation');",
                    "});",
                    "pm.collectionVariables.set('createdUserId', b.id);",
                ]),
            ]),
    request("API-05 PUT mise a jour d'un utilisateur", "PUT", "/api/users/2",
            body={"name": "morpheus", "job": "zion resident"},
            events=[tests(common(200, "updated") + [
                "const b = pm.response.json();",
                "pm.test('Valeurs mises a jour', function () {",
                "    pm.expect(b.name).to.eql('morpheus');",
                "    pm.expect(b.job).to.eql('zion resident');",
                "});",
            ])]),
    request("API-06 DELETE suppression d'un utilisateur", "DELETE", "/api/users/2",
            events=[tests(common(204) + [
                "pm.test('Corps vide', function () { pm.expect(pm.response.text()).to.eql(''); });",
            ])]),
    request("API-07 POST connexion valide", "POST", "/api/login",
            body={"email": "eve.holt@reqres.in", "password": "cityslicka"},
            events=[tests(common(200, "token") + [
                "pm.collectionVariables.set('token', pm.response.json().token);",
                "pm.test('Token non vide', function () { pm.expect(pm.collectionVariables.get('token')).to.be.a('string').and.not.empty; });",
            ])]),
    request("API-08 POST connexion sans mot de passe", "POST", "/api/login",
            body={"email": "peter@klaven"},
            description="Cas negatif : 400 'Missing password'.",
            events=[tests(common(400, "error") + [
                "pm.test('Message d erreur attendu', function () {",
                "    pm.expect(pm.response.json().error).to.eql('Missing password');",
                "});",
            ])]),
]

collection = {
    "info": {
        "_postman_id": str(uuid.uuid5(uuid.NAMESPACE_URL, "m11-reqres-collection")),
        "name": "Reqres - Tests API (M11)",
        "description": "Collection v2.1 : GET/POST/PUT/DELETE sur /api/users et /api/login. "
                       "Variables d'environnement : baseUrl, apiKey, maxResponseTime.",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    },
    "item": items,
    "variable": [
        {"key": "token", "value": ""},
        {"key": "createdUserId", "value": ""},
        {"key": "firstUserId", "value": ""},
    ],
}


def environment(name, base_url):
    return {
        "id": str(uuid.uuid5(uuid.NAMESPACE_URL, name)),
        "name": name,
        "values": [
            {"key": "baseUrl", "value": base_url, "enabled": True},
            {"key": "apiKey", "value": "reqres-free-v1", "type": "secret", "enabled": True},
            {"key": "maxResponseTime", "value": "3000", "enabled": True},
        ],
        "_postman_variable_scope": "environment",
    }


def dump(obj, filename):
    with open(os.path.join(OUT, filename), "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


dump(collection, "Reqres.postman_collection.json")
dump(environment("Reqres - public", "https://reqres.in"), "reqres-public.postman_environment.json")
dump(environment("Reqres - mock local", "http://localhost:3999"), "reqres-mock.postman_environment.json")
print("Collection et environnements generes dans", os.path.abspath(OUT))
