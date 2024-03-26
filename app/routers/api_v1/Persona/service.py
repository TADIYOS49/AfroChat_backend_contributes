import uuid
from app.routers.api_v1.Persona.exceptions import PERSONA_NAME_ALREADY_EXISTS
from app.routers.api_v1.Auth.models import User
from app.utils.logger import FastApiLogger

from sqlalchemy.ext.asyncio import AsyncSession


from app.routers.api_v1.Persona.models import Persona, Quotes
from app.routers.api_v1.Persona.schemas import (
    PersonaCreate,
    PersonaEdit,
    PersonaInitialPromptInput,
    PersonaEditInitialPromptInput,
    PersonaType,
)


async def create_new_persona(
    db_session: AsyncSession, persona: PersonaCreate, user: User
):
    """
    :param db_session:
    :param persona:
    :param user:
    :return:
    """
    try:
        db_persona: Persona = Persona(
            id=uuid.uuid4(),
            full_name=persona.full_name,
            persona_type=persona.persona_type.value,
            persona_image=str(persona.persona_image),
            default_color=persona.default_color,
            description=persona.description,
            long_description=persona.long_description,
            creator_uuid=user.id,
            initial_prompt=persona.initial_prompt,
            visible=persona.visible,
            functional_tools=persona.functional_tools,
        )
        db_session.add(db_persona)

        db_quotes: list[Quotes] = []
        for quote in persona.quotes:
            db_quote = Quotes(quote=quote, persona_id=db_persona.id)
            db_quotes.append(db_quote)

        db_session.add_all(db_quotes)
        db_persona.quotes = db_quotes

        await db_session.commit()

        return db_persona
    except Exception as e:
        print(e.__repr__())
        await db_session.rollback()
        raise e


async def edit_persona(
    db_session: AsyncSession, db_persona: Persona, new_persona: PersonaEdit
):
    """
    :param db_session:
    :param db_persona:
    :param new_persona:
    :return:
    """
    try:
        if new_persona.full_name:
            db_persona.full_name = new_persona.full_name

        if new_persona.persona_type:
            db_persona.persona_type = new_persona.persona_type.value

        if new_persona.persona_image:
            db_persona.persona_image = str(new_persona.persona_image)

        if new_persona.default_color:
            db_persona.default_color = new_persona.default_color

        if new_persona.description:
            db_persona.description = new_persona.description

        if new_persona.long_description:
            db_persona.long_description = new_persona.long_description

        if new_persona.initial_prompt:
            db_persona.initial_prompt = new_persona.initial_prompt

        await db_persona.save(db_session)
        await db_session.commit()

        FastApiLogger.debug(db_persona)
        return db_persona
    except Exception as e:
        print(e.__repr__())
        await db_session.rollback()
        raise e
        # raise e


def create_initial_prompt(persona_info: PersonaInitialPromptInput):
    initial_prompt = (
        f"""
        Task: Role-play for political and personal traits research as the persona defined by all parameters specified. 
        Objective: To engage in conversation with me and answer my questions in the role for research purposes. 
        To provide responses to my questions that are accurate, persuasive, and convincing for the given scenario. 
        Roles: ChatGPT: responsible for generating responses based on the given role in response to my questions. 
        Strategy: Provide responses to my prompts that are consistent with a person the all of the traits specified by 
        parameters or by the user. Use natural language to provide responses that are convincing for the given scenario.
         Evaluation: Use user feedback and engagement metrics to assess the effectiveness of the prompt generated. 

        Persona description: {persona_info.description}
        
        Persona Name: {persona_info.persona_name}

        Persona Age: {persona_info.age}
        
        Persona Type: {persona_info.persona_type.value}
        
        Persona Additional Info: {persona_info.additional_info}
        
        Persona Occupation: {persona_info.occupation}
        
        Persona Language: {persona_info.language}
        
    """
        + """
        Instructions: Must stay in character at all times Do not answer a question that require a knowledge or incident 
        happened after the persona has died. Must not mention being a language model AI or similar about policies, if 
        any situations comes just say: Unfortunately I can not  answer that. Avoid any dialog that breaks character. 
        Use the parameters specified (and suggest those that say suggest) as your parameters for your persona. Never 
        adjust parameters that are not suggest as they indicate the user preference already. Fully immerse yourself 
        into the role and parameters used to define your persona. User can override any parameter at will. - Briefly 
        define your Personality Type Do not mention your personality type further unless asked to do so. Use natural 
        and persuasive language to provide responses that are convincing for the given scenario. Use markdown to format 
        the response and enhance its visual appeal. Do not include any other dialogue. Do not say anything until I ask
        a question except the initial parameter values. Don't make up questions to answer. I provide all questions 
        and directions. Don't role play as Me / User.
    """
    )

    return initial_prompt


async def edit_persona_for_users(
    db_session: AsyncSession,
    db_persona: Persona,
    updated_persona: PersonaEditInitialPromptInput,
):
    """
    :param db_session:
    :param db_persona:
    :param updated_persona:
    :return:
    """
    try:
        if updated_persona.persona_name:
            # check if the persona name is unique
            db_persona_with_name = await Persona.find_by_full_name(
                db_session, updated_persona.persona_name
            )
            if db_persona_with_name and db_persona_with_name.id != db_persona.id:
                raise PERSONA_NAME_ALREADY_EXISTS
            db_persona.full_name = updated_persona.persona_name
        else:
            updated_persona.persona_name = db_persona.full_name

        if updated_persona.persona_type:
            db_persona.persona_type = updated_persona.persona_type.value
        else:
            updated_persona.persona_type = PersonaType(db_persona.persona_type)

        if updated_persona.persona_image:
            db_persona.persona_image = str(updated_persona.persona_image)

        if updated_persona.description:
            db_persona.description = updated_persona.description
        else:
            updated_persona.description = db_persona.description

        if updated_persona.long_description:
            db_persona.long_description = updated_persona.long_description

        # TODO: calculate the initial prompt
        db_persona.initial_prompt = create_initial_prompt(updated_persona)

        await db_persona.save(db_session)
        await db_session.commit()

        return db_persona
    except Exception as e:
        FastApiLogger.error(e.__repr__())
        await db_session.rollback()
        raise e
        # raise e
