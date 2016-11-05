# get session data

    form session import session_blueprint, get_session_service
    NAME = 'sessions'
    app = ...
    app.blueprint(session_blueprint, db=database, db_name=NAME, loop=None)
    
    @app.route('/')
    async def handler_get_data(request):
        # get data
        data = await get_session_service(NAME).get_request_session_data(request)
        ...
    
    @app.route('/')
    async def handler_get_data(request):
        response = ...
        data = ...
        ...
        # set data
        await get_session_service(NAME).set_request_session_data(request, response, data)
        ...
        return response
    
    
    # low lewel API
    
    async def examples():
        session = get_session_service(NAME)
        await get_session_data(uid)
        await set_session_data(uid, data)
        await update_session_data(uid, data)
